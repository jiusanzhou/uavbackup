#!/usr/bin/env python
'''
Mavproxy - a MAVLink proxy program

Copyright Andrew Tridgell 2011
Released under the GNU GPL version 3 or later

'''

import sys, os, time, socket, signal, re
import fnmatch, errno, threading
import serial, Queue, select
import subprocess
import traceback
import select

from MAVProxy.modules.lib import textconsole
from MAVProxy.modules.lib import rline
from MAVProxy.modules.lib import mp_module
from MAVProxy.modules.lib import dumpstacks

from control_module.fly_control import FlyControl
from control_module.sensor_control import Sonar, servosCtr, setPin, setupServosAndPin
from control_module.data_control import SocketIOConsole#ServerConsole

# adding all this allows pyinstaller to build a working windows executable
# note that using --hidden-import does not work for these modules
try:
	from multiprocessing import freeze_support
	from pymavlink import mavwp, mavutil
	#import matplotlib, HTMLParser
	#try:
	#	import readline
	#except ImportError:
	#	import pyreadline as readline
except Exception:
	  pass

if __name__ == '__main__':
	  freeze_support()

class MPStatus(object):
	'''hold status information about the mavproxy'''
	def __init__(self):
		self.gps	 = None
		self.msgs = {}
		self.msg_count = {}
		self.counters = {'MasterIn' : [], 'MasterOut' : 0, 'FGearIn' : 0, 'FGearOut' : 0, 'Slave' : 0}
		self.setup_mode = opts.setup
		self.mav_error = 0
		self.altitude = 0
		self.last_altitude_announce = 0.0
		self.last_distance_announce = 0.0
		self.exit = False
		self.last_mode_announce = 0
		self.logdir = None
		self.last_heartbeat = 0
		self.last_message = 0
		self.heartbeat_error = False
		self.last_apm_msg = None
		self.last_apm_msg_time = 0
		self.highest_msec = 0
		self.have_gps_lock = False
		self.lost_gps_lock = False
		self.last_gps_lock = 0
		self.watch = None
		self.last_streamrate1 = -1
		self.last_streamrate2 = -1
		self.last_seq = 0
		self.armed = False



		self.status = {}

		self.flightmode = 'MAV'

		self.manual_control = 0
		self.cmd_busy = 0

		self.camera_stream = None
		self.numUsers = 0

		self.left = 1000
		self.right = 1000
		self.front = 1000
		self.rear = 1000
		self.direction = 0

		self.started_clean = 0
		self.cleaning = 0
		self.target_point = [0, 0]


def say_text(text, priority='important'):
	'''text output - default function for say()'''
	mpstate.console.write(text, mpstate.status.flightmode)

def say(text, priority='important'):
	'''text and/or speech output'''
	if len(text) > 1:
		mpstate.functions.say(text, priority)

def add_input(cmd, immediate=False):
	'''add some command input to be processed'''
	if immediate:
		process_stdin(cmd)
	else:
		if not mpstate.manual_control:
			mpstate.input_queue.put(cmd)

class MAVFunctions(object):
	'''core functions available in modules'''
	def __init__(self):
		self.process_stdin = add_input
		self.param_set = param_set
		self.get_mav_param = get_mav_param
		self.say = say_text
		# input handler can be overridden by a module
		self.input_handler = None

class MPState(object):
	'''holds state of mavproxy'''
	def __init__(self):
		self.console = textconsole.SimpleConsole()
		self.map = None
		self.map_functions = {}
		self.vehicle_type = None
		self.vehicle_name = None
		from MAVProxy.modules.lib.mp_settings import MPSettings, MPSetting
		self.settings = MPSettings(
			[ MPSetting('link', int, 1, 'Primary Link', tab='Link', range=(0,4), increment=1),
			  MPSetting('streamrate', int, 4, 'Stream rate link1', range=(-1,20), increment=1),
			  MPSetting('streamrate2', int, 4, 'Stream rate link2', range=(-1,20), increment=1),
			  MPSetting('heartbeat', int, 1, 'Heartbeat rate', range=(0,5), increment=1),
			  MPSetting('mavfwd', bool, True, 'Allow forwarded control'),
			  MPSetting('mavfwd_rate', bool, False, 'Allow forwarded rate control'),
			  MPSetting('shownoise', bool, True, 'Show non-MAVLink data'),
			  MPSetting('baudrate', int, opts.baudrate, 'baudrate for new links', range=(0,10000000), increment=1),
			  MPSetting('rtscts', bool, opts.rtscts, 'enable flow control'),
			  MPSetting('select_timeout', float, 0.01, 'select timeout'),

			  MPSetting('altreadout', int, 10, 'Altitude Readout',
						range=(0,100), increment=1, tab='Announcements'),
			  MPSetting('distreadout', int, 200, 'Distance Readout', range=(0,10000), increment=1),

			  MPSetting('moddebug', int, opts.moddebug, 'Module Debug Level', range=(0,3), increment=1, tab='Debug'),
			  MPSetting('compdebug', int, 0, 'Computation Debug Mask', range=(0,3), tab='Debug'),
			  MPSetting('flushlogs', bool, False, 'Flush logs on every packet'),
			  MPSetting('requireexit', bool, False, 'Require exit command'),
			  MPSetting('wpupdates', bool, True, 'Announce waypoint updates'),

			  MPSetting('basealt', int, 0, 'Base Altitude', range=(0,30000), increment=1, tab='Altitude'),
			  MPSetting('wpalt', int, 100, 'Default WP Altitude', range=(0,10000), increment=1),
			  MPSetting('rallyalt', int, 90, 'Default Rally Altitude', range=(0,10000), increment=1),
			  MPSetting('terrainalt', str, 'Auto', 'Use terrain altitudes', choice=['Auto','True','False']),
			  MPSetting('rally_breakalt', int, 40, 'Default Rally Break Altitude', range=(0,10000), increment=1),
			  MPSetting('rally_flags', int, 0, 'Default Rally Flags', range=(0,10000), increment=1),

			  MPSetting('source_system', int, 255, 'MAVLink Source system', range=(0,255), increment=1, tab='MAVLink'),
			  MPSetting('source_component', int, 0, 'MAVLink Source component', range=(0,255), increment=1),
			  MPSetting('target_system', int, 0, 'MAVLink target system', range=(0,255), increment=1),
			  MPSetting('target_component', int, 0, 'MAVLink target component', range=(0,255), increment=1),
			  MPSetting('state_basedir', str, None, 'base directory for logs and aircraft directories')
			])

		self.completions = {
			"script"		 : ["(FILENAME)"],
			"set"			: ["(SETTING)"],
			"status"		 : ["(VARIABLE)"],
			"module"	: ["list",
						   "load (AVAILMODULES)",
						   "<unload|reload> (LOADEDMODULES)"]
			}

		self.status = MPStatus()

		# master mavlink device
		self.mav_master = None

		# mavlink outputs
		self.mav_outputs = []

		# SITL output
		self.sitl_output = None
		self.mav_param = mavparm.MAVParmDict()
		self.modules = []
		self.public_modules = {}
		self.functions = MAVFunctions()
		self.select_extra = {}
		self.continue_mode = False
		self.aliases = {}

		self.manual_control = 0
		self.flycontrol = None
		self.datacontrol = None
		self.cmd_busy = 0

		self.server_command_map = {}

		self.aircraftname = "NO.1"

		self.socketIO = None
		self.camera_stream_process = None
		self.camera_stream_thread = None

		import platform
		self.system = platform.system()

	def module(self, name):
		'''Find a public module (most modules are private)'''
		if name in self.public_modules:
			return self.public_modules[name]
		return None

	def master(self):
		'''return the currently chosen mavlink master object'''
		if len(self.mav_master) == 0:
			  return None
		if self.settings.link > len(self.mav_master):
			self.settings.link = 1

		# try to use one with no link error
		if not self.mav_master[self.settings.link-1].linkerror:
			return self.mav_master[self.settings.link-1]
		for m in self.mav_master:
			if not m.linkerror:
				return m
		return self.mav_master[self.settings.link-1]

def get_mav_param(param, default=None):
	'''return a EEPROM parameter value'''
	return mpstate.mav_param.get(param, default)

def param_set(name, value, retries=3):
	'''set a parameter'''
	name = name.upper()
	return mpstate.mav_param.mavset(mpstate.master(), name, value, retries=retries)



def load_module(modname, quiet=True):
	'''load a module'''
	modpaths = ['MAVProxy.modules.mavproxy_%s' % modname, modname]
	#for (m,pm) in mpstate.modules:
	#	if m.name == modname:
	#		if not quiet:
	#			print("module %s already loaded" % modname)
	#		return False
	for modpath in modpaths:
		try:
			m = import_package(modpath)
			reload(m)
			module = m.init(mpstate)
			if isinstance(module, mp_module.MPModule):
				mpstate.modules.append((module, m))
				return True
			else:
				ex = "%s.init did not return a MPModule instance" % modname
				break
		except ImportError as msg:
			ex = msg
			if mpstate.settings.moddebug > 1:
				import traceback
				print(traceback.format_exc())
	return False

def unload_module(modname):
	'''unload a module'''
	for (m,pm) in mpstate.modules:
		#print m.name
		if m.name == modname:
			if hasattr(m, 'unload'):
				m.unload()
			mpstate.modules.remove((m,pm))
			print("Unloaded module %s" % modname)
			return True
	print("Unable to find module %s" % modname)
	return False


def clear_zipimport_cache():
	"""Clear out cached entries from _zip_directory_cache.
	See http://www.digi.com/wiki/developer/index.php/Error_messages"""
	import sys, zipimport
	syspath_backup = list(sys.path)
	zipimport._zip_directory_cache.clear()

	# load back items onto sys.path
	sys.path = syspath_backup
	# add this too: see https://mail.python.org/pipermail/python-list/2005-May/353229.html
	sys.path_importer_cache.clear()

# http://stackoverflow.com/questions/211100/pythons-import-doesnt-work-as-expected
# has info on why this is necessary.

def import_package(name):
	"""Given a package name like 'foo.bar.quux', imports the package
	and returns the desired module."""
	import zipimport
	#print name
	try:
		mod = __import__(name)
	except ImportError:
		clear_zipimport_cache()
		mod = __import__(name)

	components = name.split('.')
	for comp in components[1:]:
		mod = getattr(mod, comp)
	return mod


command_map = {}

def process_from_servers(line):
	pass

def process_stdin(line):
	'''handle commands from user'''
	if line is None:
		sys.exit(0)

	# allow for modules to override input handling
	if mpstate.functions.input_handler is not None:
		mpstate.functions.input_handler(line)
		return

	line = line.strip()

	if not line:
		return

	args = line.split()
	cmd = args[0]
	#while cmd in mpstate.aliases:
	#	 line = mpstate.aliases[cmd]
	#	 args = line.split() + args[1:]
	#	 cmd = args[0]

	if cmd == 'test':
		print("\n")
		res = mpstate.status.status
		for i in res:
			print("%-15s : %s"%(i, res[i]))
		return

	if cmd == 'hh':
		print("Starting...")
		if len(args) > 1:
			test(args[1])
		return

	if cmd == 'help':
		k = command_map.keys()
		k.sort()
		for cmd in k:
			fn = command_map[cmd]
			print("%-20s : %s" % (cmd, help))
		print command_map.keys()
		return
	if cmd == 'exit' and mpstate.settings.requireexit:
		mpstate.status.exit = True
		return

	if not cmd in command_map:
		for (m,pm) in mpstate.modules:
			if hasattr(m, 'unknown_command'):
				try:
					if m.unknown_command(args):
						return
				except Exception as e:
					print("ERROR in command: %s" % str(e))
		print("Unknown command '%s'" % line)
		return
	fn = command_map[cmd]
	try:
		#print args
		fn(args[1:])
	except Exception as e:
		print("ERROR in command %s: %s" % (args[1:], str(e)))
		if mpstate.settings.moddebug > 1:
			traceback.print_exc()

def test(args):
	fn = {
	# 	"up": mpstate.flycontrol.move_up,
	# 	"down": mpstate.flycontrol.move_down,
	# 	"left": mpstate.flycontrol.move_left,
	# 	"right": mpstate.flycontrol.move_right,
	# 	"front": mpstate.flycontrol.move_front,
	# 	"rear": mpstate.flycontrol.move_rear,
		"arm": mpstate.flycontrol.arm,
		"disarm": mpstate.flycontrol.disarm,
		"takeoff": mpstate.flycontrol.takeoff,
		"land": mpstate.flycontrol.land,
		"clear_rc": mpstate.flycontrol.clear_rc
	}
	if args in ["rear", "front", "down", "up", "right", "left"]:
		#print(args[0])
		if not mpstate.cmd_busy:
			mpstate.cmd_busy = 1
			# d()
			mpstate.flycontrol.move(args)
			mpstate.cmd_busy = 0
		return
	d = fn.get(args[0], None)
	if d:
		if not mpstate.cmd_busy:
			mpstate.cmd_busy = 1
			d()
			mpstate.cmd_busy = 0


def update_aircraft_status():
	sonar = Sonar()
	while 1:
		# left = threading.Thread(target=sonar.measure, args=("left", ))
		# left.start()
		# left.join(2)

		# right = threading.Thread(target=sonar.measure, args=("right", ))
		# right.start()
		# right.join(2)

		front = threading.Thread(target=sonar.measure, args=("front", ))
		front.start()
		front.join(2)
		if mpstate.status.front < 1:
			mpstate.status.started_clean = 1
		else:
			mpstate.status.started_clean = 0
		# rear = threading.Thread(target=sonar.measure, args=("rear", ))
		# rear.start()
		# rear.join(2)

def auto_control_loop():
	pass


def process_master(m):
	'''process packets from the MAVLink master'''
	try:
		s = m.recv(16*1024)
	except Exception:
		time.sleep(0.1)
		return
	if len(s) == 0:
		time.sleep(0.1)
		return
	if mpstate.logqueue_raw:
		mpstate.logqueue_raw.put(str(s))
	if m.first_byte and opts.auto_protocol:
		m.auto_mavlink_version(s)
	msgs = m.mav.parse_buffer(s)
	if msgs:
		for msg in msgs:
			if getattr(m, '_timestamp', None) is None:
				m.post_message(msg)
			if msg.get_type() == "BAD_DATA":
				if opts.show_errors:
					mpstate.console.write("MAV error: %s" % msg, mpstate.status.flightmode)
				mpstate.status.mav_error += 1

def process_mavlink(slave):
	'''process packets from MAVLink slaves, forwarding to the master'''
	try:
		buf = slave.recv()
	except socket.error:
		return
	try:
		if slave.first_byte and opts.auto_protocol:
			slave.auto_mavlink_version(buf)
		msgs = slave.mav.parse_buffer(buf)
	except mavutil.mavlink.MAVError as e:
		mpstate.console.write("Bad MAVLink slave message from %s: %s" % (slave.address, e.message), mpstate.status.flightmode)
		return
	if msgs is None:
		return
	if mpstate.settings.mavfwd and not mpstate.status.setup_mode:
		for m in msgs:
			if mpstate.status.watch is not None:
				if fnmatch.fnmatch(m.get_type().upper(), mpstate.status.watch.upper()):
					mpstate.console.write(str(m), mpstate.status.flightmode)
			mpstate.master().write(m.get_msgbuf())
	mpstate.status.counters['Slave'] += 1

def mkdir_p(dir):
	'''like mkdir -p'''
	if not dir:
		return
	if dir.endswith("/"):
		mkdir_p(dir[:-1])
		return
	if os.path.isdir(dir):
		return
	mkdir_p(os.path.dirname(dir))
	os.mkdir(dir)

def log_writer():
	'''log writing thread'''
	while True:
		mpstate.logfile_raw.write(mpstate.logqueue_raw.get())
		while not mpstate.logqueue_raw.empty():
			mpstate.logfile_raw.write(mpstate.logqueue_raw.get())
		while not mpstate.logqueue.empty():
			mpstate.logfile.write(mpstate.logqueue.get())
		if mpstate.settings.flushlogs:
			mpstate.logfile.flush()
			mpstate.logfile_raw.flush()

# If state_basedir is NOT set then paths for logs and aircraft
# directories are relative to mavproxy's cwd
def log_paths():
	'''Returns tuple (logdir, telemetry_log_filepath, raw_telemetry_log_filepath)'''
	logname = os.path.basename(opts.logfile)
	dir_path = os.path.dirname(opts.logfile)
	if not os.path.isabs(dir_path) and mpstate.settings.state_basedir is not None:
		dir_path = os.path.join(mpstate.settings.state_basedir,dir_path)
	logdir = dir_path

	mkdir_p(logdir)
	return (logdir,
			os.path.join(logdir, logname),
			os.path.join(logdir, logname + '.raw'))


def open_telemetry_logs(logpath_telem, logpath_telem_raw):
	'''open log files'''
	if opts.append_log or opts.continue_mode:
		mode = 'a'
	else:
		mode = 'w'
	mpstate.logfile = open(logpath_telem, mode=mode)
	mpstate.logfile_raw = open(logpath_telem_raw, mode=mode)
	print("Log Directory: %s" % mpstate.status.logdir)
	print("Telemetry log: %s" % logpath_telem)

	# use a separate thread for writing to the logfile to prevent
	# delays during disk writes (important as delays can be long if camera
	# app is running)
	t = threading.Thread(target=log_writer, name='log_writer')
	t.daemon = True
	t.start()

def set_stream_rates():
	'''set mavlink stream rates'''
	if (not msg_period.trigger() and
		mpstate.status.last_streamrate1 == mpstate.settings.streamrate and
		mpstate.status.last_streamrate2 == mpstate.settings.streamrate2):
		return
	mpstate.status.last_streamrate1 = mpstate.settings.streamrate
	mpstate.status.last_streamrate2 = mpstate.settings.streamrate2
	master = mpstate.mav_master[0]
	if master.linknum == 0:
		rate = mpstate.settings.streamrate
	else:
		rate = mpstate.settings.streamrate2
	if rate != -1:
		master.mav.request_data_stream_send(mpstate.settings.target_system, mpstate.settings.target_component,
											mavutil.mavlink.MAV_DATA_STREAM_ALL,
											rate, 1)

def check_link_status():
	'''check status of master links'''
	tnow = time.time()
	if mpstate.status.last_message != 0 and tnow > mpstate.status.last_message + 5:
		say("no link")
		mpstate.status.heartbeat_error = True
	master = mpstate.mav_master[0]
	if not master.linkerror and (tnow > master.last_message + 5 or master.portdead):
		say("link %u down" % (master.linknum+1))
		master.linkerror = True

def send_heartbeat(master):
	if master.mavlink10():
		master.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID,
								  0, 0, 0)
	else:
		MAV_GROUND = 5
		MAV_AUTOPILOT_NONE = 4
		master.mav.heartbeat_send(MAV_GROUND, MAV_AUTOPILOT_NONE)

def periodic_tasks():
	'''run periodic checks'''
	if mpstate.status.setup_mode:
		return

	if (mpstate.settings.compdebug & 2) != 0:
		return

	if mpstate.settings.heartbeat != 0:
		heartbeat_period.frequency = mpstate.settings.heartbeat

	if heartbeat_period.trigger() and mpstate.settings.heartbeat != 0:
		mpstate.status.counters['MasterOut'] += 1
		send_heartbeat(mpstate.mav_master[0])

	if heartbeat_check_period.trigger():
		pass
		#check_link_status()

	set_stream_rates()

	# call optional module idle tasks. These are called at several hundred Hz
	for (m,pm) in mpstate.modules:
		if hasattr(m, 'idle_task'):
			try:
				m.idle_task()
			except Exception as msg:
				if mpstate.settings.moddebug == 1:
					print(msg)
				elif mpstate.settings.moddebug > 1:
					exc_type, exc_value, exc_traceback = sys.exc_info()
					traceback.print_exception(exc_type, exc_value, exc_traceback,
											  limit=2, file=sys.stdout)

		# also see if the module should be unloaded:
		if m.needs_unloading:
			unload_module(m.name)

def get_status(name1=None, name2=None):

	if name1 and name2:
		try:
			_v1 = mpstate.status.msgs.get(name1, '')
			_v2 = re.compile('%s : (\d+)' % name2).findall(str(_v1))[0]
		except Exception, e:
			_v2 = ""
		return _v2
	else:
		res = {}
		for key in mpstate.status.msgs.keys():
			_r = {}
			_v = str(mpstate.status.msgs[key]).split(", ")
			_kone = re.search("(.+) {(.+)", _v[0])
			try:
				_k = _kone.group(1)
				_v[0] = _kone.group(2)
			except Exception, e:
				continue
			_v[-1] = _v[-1][:-1]
			for i in _v:
				_i = i.split(" : ")
				try:
					if name1 == key and name2 == _i[0]:
						return _i[1]
					_r[_i[0]] = _i[1]
				except Exception, e:
					continue
			if (not name2) and (name1 == key):
				return _r
			res[_k] = _r
		return res

def manual_control_logic(chan6_raw_flag):
	'''
	Control the logic of remote controller

	'''
	try:
		chan6_raw = int(get_status("RC_CHANNELS_RAW", "chan6_raw"))
	except Exception, e:
		chan6_raw = 1600
	
	if chan6_raw < 1300:
		if chan6_raw_flag:
			mpstate.flycontrol.clear_rc()
			mpstate.manual_control = 1
		return 0
	else:
		mpstate.manual_control = 0
		return 1

def main_loop():
	'''main processing loop'''
	if not mpstate.status.setup_mode and not opts.nowait:
		master = mpstate.mav_master[0]
		send_heartbeat(master)
		if master.linknum == 0:
			print("Waiting for heartbeat from %s" % master.address)
			mpstate.console.write("Waiting for heartbeat", mpstate.status.flightmode)
			master.wait_heartbeat()
		set_stream_rates()

	chan6_raw_flag = 1

	while 1 and (not mpstate.status.exit):

		if mpstate is None or mpstate.status.exit:
			return

		chan6_raw_flag = manual_control_logic(chan6_raw_flag) # manual control

		while not mpstate.input_queue.empty():
			line = mpstate.input_queue.get()
			mpstate.input_count += 1
			cmds = line.split(';')
			if len(cmds) == 1 and cmds[0] == "":
				  mpstate.empty_input_count += 1
			for c in cmds:
				process_stdin(c)

		master = mpstate.mav_master[0]
		if master.fd is None:
			if master.port.inWaiting() > 0:
				process_master(master)

		periodic_tasks()

		rin = []
		master = mpstate.mav_master[0]
		if master.fd is not None and not master.portdead:
			rin.append(master.fd)

		if rin == []:
			time.sleep(0.0001)
			continue

		for fd in mpstate.select_extra:
			rin.append(fd)
		try:
			(rin, win, xin) = select.select(rin, [], [], mpstate.settings.select_timeout)
		except select.error:
			continue

		if mpstate is None:
			return

		
		mpstate.status.status = get_status()		


		#mpstate.socketIO.emit("update status", str(needed_status())) if mpstate.socketIO else None # Update aircraft status

		for fd in rin:
			if mpstate is None:
				  return
			master = mpstate.mav_master[0]
			if fd == master.fd:
				process_master(master)
				if mpstate is None:
					return
				continue

			# this allow modules to register their own file descriptors
			# for the main select loop
			if fd in mpstate.select_extra:
				try:
					# call the registered read function
					(fn, args) = mpstate.select_extra[fd]
					fn(args)
				except Exception as msg:
					if mpstate.settings.moddebug == 1:
						print(msg)
					# on an exception, remove it from the select list
					mpstate.select_extra.pop(fd)

def input_loop():
	'''wait for user input'''
	while mpstate.status.exit != True:
		try:
			if mpstate.status.exit != True:
				##print()
				line = raw_input(mpstate.rl.prompt)
		except EOFError:
			mpstate.status.exit = True
			sys.exit(1)
		mpstate.input_queue.put(line)


def needed_status():
	c = {}
	r = mpstate.status.status
	if r:
		try:
			_s = r.get('SYS_STATUS', None)
			if _s:
				c["s"] = {
					"c": _s['current_battery'],
					"v": _s['voltage_battery']
				}
				_s = r['RC_CHANNELS_RAW']
				c["c"] = {
					"1": _s['chan1_raw'],
					"2": _s['chan2_raw'],
					"3": _s['chan3_raw'],
					"4": _s['chan4_raw'],
					"5": _s['chan5_raw'],
					"6": _s['chan6_raw'],
					"7": _s['chan7_raw'],
					"8": _s['chan8_raw']
				}
				_s = r['GLOBAL_POSITION_INT']
				c["g"] = {
					"o": _s['lon'],
					"a": _s['lat'],
					"d": _s['hdg'],
					"h": _s['relative_alt']
				}
				_s = r['RAW_IMU']
				c["i"] = {
					"za": _s['zacc'],
					"xa": _s['xacc'],
					"ya": _s['yacc']
				}
		except:
			pass
	return c





def camera_stream(*args):
	(name, width, height) = args
	cmd = ['ffmpeg', '-s', '%sx%s' % (width, height), '-f', \
		'video4linux2', '-i', '/dev/video0', '-f', \
		'mpeg1video', '-b:v', '500k', '-r', '30', \
		'udp://%s:%s' % (mpstate.udp_video_server[0], mpstate.udp_video_server)]
	mpstate.camera_stream_process = subprocess.Popen(cmd)


def socketIOClient():

	def on_new_commands(cmd):
		mpstate.input_queue.put(cmd)

	def on_user_joined_left(data):		
		mpstate.status.numUsers = data['numUsers']

	def on_stop_camera_stream():
		if mpstate.status.numUsers < 1:
			mpstate.camera_stream_process.kill() if mpstate.camera_stream_process else None
			print('End stream thread...')

	def on_start_camera_stream(data):
		_d = data
		name = _d.get('name', '')
		width = _d.get('width', '')
		height = _d.get('height', '')
		if (mpstate.status.numUsers > 0) and name and width and height:
			mpstate.camera_stream_thread = threading.Thread(target=camera_stream, args=(name, width, height), name='camera_stream')
			mpstate.camera_stream_thread.daemon = True
			mpstate.camera_stream_thread.start()

	try:
		from socketIO_client import SocketIO, LoggingNamespace

		mpstate.socketIO = SocketIO(mpstate.socket_server[0], mpstate.socket_server[1], LoggingNamespace)
		mpstate.socketIO.on('new command', on_new_commands)
		mpstate.socketIO.on('start camera stream', on_start_camera_stream)
		mpstate.socketIO.on('user left', on_user_joined_left)
		mpstate.socketIO.on('user joined', on_user_joined_left)

		mpstate.socketIO.wait()
	except Exception, e:
		print("Error while connectting to socket server\n%s"%e)
		#pass




def send_status_by_sokcet():
	count = 0
	_angle = 0
	while 1:

		# when to start cleaning


		if mpstate.status.started_clean and not mpstate.status.cleaning:
			count += 1
			if count > 4:
				servosCtr(mpstate.updown_servos_pin, 60 + 10 * (i + 1))
				setPin(mpstate.clean_servos_pin, 1)
				print("Start clean")
				mpstate.status.cleaning = 1
		elif mpstate.status.cleaning and not mpstate.status.started_clean:
			count -=1
			if count == 0:
				setPin(mpstate.clean_servos_pin, 0)
				servosCtr(mpstate.updown_servos_pin, 160 - 10 * (i + 1))
				print("End clean")
				mpstate.status.cleaning = 0

		servosCtr(mpstate.sonar_servos_pin, _angle)
		_angle += 30

		#mpstate.socketIO.emit("update status", str(needed_status())) if mpstate.socketIO else None
		if mpstate.socketIO:
			mpstate.socketIO.emit("update status", str(needed_status()))
			#print("Sended status...")
		else:
			pass
			#print("No send status...")
		time.sleep(1)

class death_options(object):

	''' This is for mpstate's options '''
	master = [
		"/dev/ttyO4",
		"/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller-if00-port0", 
		"/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0",
	]

	sonar_servos_pin = "P8_13"
	updown_servos_pin = "P9_14"
	clean_servos_pin = "P9_15"

	socket_server = ('192.168.7.1', 3000)
	udp_video_server = ('192.168.7.1', 2009)

	output = []
	baudrate = 57600
	streamrate = 4
	sitl = None
	SOURCE_SYSTEM = 255
	SOURCE_COMPONENT = 0
	TARGET_SYSTEM = 0
	TARGET_COMPONENT = 0
	logfile = 'mav.tlog'
	append_log = True
	quadcopter = False
	setup = False
	nodtr = False
	show_errors = False
	auto_protocol = False
	nowait = False
	continue_mode = False
	dialect = "ardupilotmega"
	rtscts = None
	moddebug = 0
	mission = None
	daemon = False
	default_modules = ["log","wp","rally","fence","param","relay","tuneopt","arm","mode","calibration","rc","auxopt","misc","cmdlong","battery","terrain","output"]


	def __init__(self, **kwargs):
		for i in kwargs:
			setattr(self, i, kwargs[i])

if __name__ == '__main__':

	#opts = add_options()
	opts = death_options()

	from pymavlink import mavutil, mavparm
	mavutil.set_dialect(opts.dialect)

	mpstate = MPState()
	#import Adafruit_BBIO.UART as UART
	#UART.setup("UART4")

	mpstate.sonar_servos_pin = opts.sonar_servos_pin
	mpstate.updown_servos_pin = opts.updown_servos_pin
	mpstate.clean_servos_pin = opts.clean_servos_pin

	mpstate.socket_server = opts.socket_server
	mpstate.udp_video_server = opts.udp_video_server

	setupServosAndPin(opts.updown_servos_pin, opts.sonar_servos_pin, opts.clean_servos_pin, 60, 90)


	mpstate.status.exit = False
	mpstate.command_map = command_map
	mpstate.continue_mode = opts.continue_mode
	# queues for logging
	mpstate.logqueue = Queue.Queue()
	mpstate.logqueue_raw = Queue.Queue()

	# container for status information
	mpstate.settings.target_system = opts.TARGET_SYSTEM
	mpstate.settings.target_component = opts.TARGET_COMPONENT

	mpstate.mav_master = []



	mpstate.rl = rline.rline("MAV>", mpstate)

	def quit_handler(signum = None, frame = None):
		#print 'Signal handler called with signal', signum
		if mpstate.status.exit:
			print 'Clean shutdown impossible, forcing an exit'
			sys.exit(0)
		else:
			mpstate.status.exit = True

	# Listen for kill signals to cleanly shutdown modules
	fatalsignals = [signal.SIGTERM]
	try:
		fatalsignals.append(signal.SIGHUP)
		fatalsignals.append(signal.SIGQUIT)
	except Exception:
		pass
	if opts.daemon: # SIGINT breaks readline parsing - if we are interactive, just let things die
		fatalsignals.append(signal.SIGINT)

	for sig in fatalsignals:
		signal.signal(sig, quit_handler)

	load_module('link', quiet=True)

	mpstate.settings.source_system = opts.SOURCE_SYSTEM
	mpstate.settings.source_component = opts.SOURCE_COMPONENT

	if not mpstate.module('link').link_add(opts.master[0]):
		sys.exit(1)

	#I will put the data out by this#
	if opts.sitl:
		mpstate.sitl_output = mavutil.mavudp(opts.sitl, input=False)

	mpstate.settings.streamrate = opts.streamrate
	mpstate.settings.streamrate2 = opts.streamrate

	msg_period = mavutil.periodic_event(1.0/15)
	heartbeat_period = mavutil.periodic_event(1)
	heartbeat_check_period = mavutil.periodic_event(0.33)

	mpstate.input_queue = Queue.Queue()
	mpstate.input_count = 0
	mpstate.empty_input_count = 0

	# call this early so that logdir is setup based on --aircraft
	(mpstate.status.logdir, logpath_telem, logpath_telem_raw) = log_paths()

	#standard_modules = opts.default_modules.split(',')
	for m in opts.default_modules:
		load_module(m, quiet=True)

	for i in command_map:
		command_map[i] = command_map[i][0]

	# log all packets from the master, for later replay
	open_telemetry_logs(logpath_telem, logpath_telem_raw)

	mpstate.flycontrol = FlyControl(cmd_map = command_map, status = mpstate.status, input_queue = mpstate.input_queue)
	#mpstate.datacontrol = DataControl(mpstate.status.msgs)
	#mpstate.console = ServerConsole(status = mpstate.status, input_queue = mpstate.input_queue)

	socket_io = threading.Thread(target=socketIOClient, name='socket io heart')
	socket_io.daemon = True
	socket_io.start()

	time.sleep(5) # wait for socket server connect

	mpstate.socketIO.emit('aircraft connected', mpstate.aircraftname) if mpstate.socketIO else None
	mpstate.console = SocketIOConsole(socketIO=mpstate.socketIO, status = mpstate.status, addr=mpstate.socket_server)


	mpstate.server_command_map = {
		"arm": mpstate.flycontrol.arm,
		"disarm": mpstate.flycontrol.disarm,
		"takeoff": mpstate.flycontrol.takeoff,
		"return": mpstate.flycontrol.return_home,
		"waypoint": mpstate.flycontrol.waypoint,
		"cancle": mpstate.flycontrol.return_home
	}


	#server_heart = threading.Thread(target=mpstate.console.send_heart, name='server_heart')
	#server_heart.daemon = True
	#server_heart.start()
	# run main loop as a thread
	mpstate.status.thread = threading.Thread(target=main_loop, name='main_loop')
	mpstate.status.thread.daemon = True
	mpstate.status.thread.start()

	send_status = threading.Thread(target=send_status_by_sokcet, name='send_status_by_socket')
	send_status.daemon = True
	send_status.start()

	# sonar = Sonar()

	update_mpstate_status = threading.Thread(target=update_aircraft_status, name='update_mpstate_status')
	update_mpstate_status.daemon = True
	update_mpstate_status.start()


	auto_fly_thread = threading.Thread(target=mpstate.flycontrol.auto_fly, name="auto_fly_thread")
	auto_fly_thread.daemon = True
	auto_fly_thread.start()

	# use main program for input. This ensures the terminal cleans
	# up on exit
	while (mpstate.status.exit != True):
		try:
			if opts.daemon:
				time.sleep(0.1)
			else:
				input_loop()
		except KeyboardInterrupt:
			# if mpstate.settings.requireexit:
			# 	print("Interrupt caught.  Use 'exit' to quit MAVProxy.")

			# 	#Just lost the map and console, get them back:
			# 	for (m,pm) in mpstate.modules:
			# 		if m.name in ["map", "console"]:
			# 			if hasattr(m, 'unload'):
			# 				try:
			# 					m.unload()
			# 				except Exception:
			# 					pass
			# 			reload(m)
			# 			m.init(mpstate)

			# else:
			mpstate.status.exit = True
			mpstate.socketIO.emit('aircraft disconnect', mpstate.aircraftname) if mpstate.socketIO else None
			sys.exit(1)

	#this loop executes after leaving the above loop and is for cleanup on exit
	for (m,pm) in mpstate.modules:
		if hasattr(m, 'unload'):
			print("Unloading module %s" % m.name)
			m.unload()

	sys.exit(1)

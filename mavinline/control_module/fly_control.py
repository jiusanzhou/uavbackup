#!/usr/bin/env python
'''
Flying controler

'''
import time

class FlyControl(object):
	"""docstring for FlyControl"""


	time = time #package

	step_rc1 = 100
	step_rc2 = 100
	step_rc3 = 200

	middle = 1220
	middle_rc3 = 1220

	lowest_rc3 = 1100

	default_time = 1
	change_speed = 0.02
	keep_time = 0.2

	now_rc1 = middle
	now_rc2 = middle
	now_rc3 = middle
	now_rc4 = middle


	left_min = 20
	right_min = 20
	rear_min = 20
	front_min = 20
	front_max = 10


	directions = {
		"right": (1, "+"),
		"left": (1, "-"),
		"front": (2, "+"),
		"rear": (2, "-"),
		"up": (3, "+"),
		"down": (3, "-")
	}

	def __init__(self, cmd_map, status, input_queue):
		super(FlyControl, self).__init__()
		self.cmd_map = cmd_map
		self.status = status
		self.input_queue = input_queue

		#from .sensor_control import Sonar
		# import sensor_control
		# self.sensor_control = sensor_control

	def _wait_until_notbusy(target_func):

		def over_time(signum, frame):
			print("Over time")
			raise AssertionError 

		def __wait_until_notbusy(*v, **kw):
			sel = v[0]
			print("who do this?")
			#sel.signal.signal(signal.SIGALRM, over_time)
			#sel.signal.alarm(2)
			while sel.status.cmd_busy:
			#print("arm busy...")
				pass
			#sel.signal.alarm(0)

			sel.status.cmd_busy += 1
			target_func(*v, **kw)
			sel.status.cmd_busy -= 1
			return target_func
		return __wait_until_notbusy

	#@_wait_until_notbusy
	def for_bug():
		pass

	#@_wait_until_notbusy
	def control(self, rc, value, _time, change_speed):
		if not self.status.manual_control:
			for i in range(1, value + 1):
				self.cmd_map["rc"]([str(rc), self.middle + i])
				time.sleep(change_speed)
			if _time != 0:
				self.time.sleep(_time if _time else self.keep_time)
				self._set_middle("3")

	#@_wait_until_notbusy
	def arm(self):
		''' Arm aircraft '''
		#self._update_middle_value()
		if not self.status.manual_control:
			self.clear_rc()
			self.time.sleep(0.1)
			self._update_middle_value()
			self.change_mode("STABILIZE")
			while self.status.flightmode != "STABILIZE":
				pass
			self.cmd_map["arm"](["throttle"])
			#self.time.sleep(self.default_time)
			#self.change_mode("loiter")
				
	#@_wait_until_notbusy
	def disarm(self):
		''' Disarm aircraft '''
		if not self.status.manual_control:
			self.cmd_map["disarm"]([])
				
	#@_wait_until_notbusy
	def clear_rc(self):
		''' clear rc for remote controler '''
		self.cmd_map["rc"](["all", "0"])
		print("Clear all RC")
				
	def _update_middle_value(self):
		self.now_rc1 = self.now_rc2 = self.now_rc3 = self.now_rc4 = self.middle = int(self.status.status["RC_CHANNELS_RAW"]["chan1_raw"])
		self.lowest_rc3 = int(self.status.status["RC_CHANNELS_RAW"]["chan3_raw"])
				
	#@_wait_until_notbusy
	def land(self):
		''' for land '''
		if not self.status.manual_control:
			self.cmd_map["mode"](["land"])
				
	#@_wait_until_notbusy
	def takeoff(self):
		if not self.status.manual_control and self.status.armed:
			if self.status.status["GPS_RAW_INT"]["lon"] == "0":
				print("No GPS Data, Can't auto takeoff!")
				return
			self.change_mode("GUIDED")
			while self.status.flightmode != "GUIDED":
				pass
			self.cmd_map["takeoff"](["1"])
			time.sleep(2)
			self.cmd_map["rc"](["3", "1220"])
			self.change_mode("loiter")
				
	#@_wait_until_notbusy
	def change_mode(self, mode):
		''' change the fly mode '''
		mode = mode.upper()
		if not self.status.manual_control:
			default_modes = ['RTL', 'POSHOLD', 'LAND', 'OF_LOITER', 'STABILIZE', 'AUTO', 'GUIDED', 'DRIFT', 'FLIP', 'AUTOTUNE', 'ALT_HOLD', 'LOITER', 'POSITION', 'CIRCLE', 'SPORT', 'ACRO']
			if mode in default_modes:
				self.cmd_map["mode"](["%s" % mode])
				
	#@_wait_until_notbusy
	def set_velocity(self, **kwargs):
		if not self.status.manual_control:
			pass
				
	#@_wait_until_notbusy
	def yaw_left(self, status, angle):
		if not self.status.manual_control:
			pass
				
	#@_wait_until_notbusy
	def yaw_right(self, status, angle):
		if not self.status.manual_control:
			pass
				
	#@_wait_until_notbusy
	def control_rc3(self, rc_value):
		if not self.status.manual_control:
			self.cmd_map["rc"](["3", rc_value])
			#time.sleep(time if time else self.default_time)
			#self._set_middle("3")
				
	#@_wait_until_notbusy
	def move_down(self, _time = None):
		if not self.status.manual_control:
			for i in range(0, self.step_rc3 + 1, 2):
				_v = self.middle - i
				self.control_rc3(_v)
				self.time.sleep(self.change_speed)
				self.now_rc3 = _v
			if _time != 0:
				self.time.sleep(_time if _time else self.keep_time)
				self._set_middle("3")
				
	#@_wait_until_notbusy
	def move_up(self, _time = None):
		if not self.status.manual_control:
			for i in range(0, self.step_rc3 + 1, 2):
				_v = self.middle + i
				self.control_rc3(_v)
				self.time.sleep(self.change_speed)
				self.now_rc3 = _v
			if _time != 0:
				self.time.sleep(_time if _time else self.keep_time)
				self._set_middle("3")
				
	#@_wait_until_notbusy
	def move_left(self, _time = None):
		if not self.status.manual_control:
			for i in range(0, self.step_rc1 + 1, 2):
				_v = self.middle - i
				self.cmd_map["rc"](["1", _v])
				self.time.sleep(self.change_speed)
				self.now_rc1 = _v
			if _time != 0:
				self.time.sleep(_time if _time else self.keep_time)
				self._set_middle("1")
				
	#@_wait_until_notbusy		
	def move_right(self, _time = None):
		if not self.status.manual_control:
			for i in range(0, self.step_rc1 + 1, 2):
				_v = self.middle + i			
				self.cmd_map["rc"](["1", _v])
				self.time.sleep(self.change_speed)
				self.now_rc1 = _v
			if _time != 0:
				self.time.sleep(_time if _time else self.keep_time)
				self._set_middle("1")
				
	#@_wait_until_notbusy		
	def move_rear(self, _time = None):
		if not self.status.manual_control:
			for i in range(0, self.step_rc2 + 1, 2):
				_v = self.middle - i
				self.cmd_map["rc"](["2", _v])
				self.time.sleep(self.change_speed)
				self.now_rc2 = _v
			if _time != 0:
				self.time.sleep(_time if _time else self.keep_time)
				self._set_middle("2")
				
	#@_wait_until_notbusy
	def move_front(self, _time = None):
		if not self.status.manual_control:
			for i in range(0, self.step_rc2 + 1, 2):
				_v = self.middle + i
				self.cmd_map["rc"](["2", _v])
				self.time.sleep(self.change_speed)
				self.now_rc2 = _v
			if _time != 0:
				self.time.sleep(_time if _time else self.keep_time)
				self._set_middle("2")



	def return_home(self):
		# Turn the cleaner
		self.change_mode("RTL")

	def waypoint(self):
		pass





	def move(self, direct, _time = None):
		if not self.status.manual_control:
			_do = self.get("directions", None)
			if _do:
				_d = _do[0]
				_o = _do[1]
				for i in range(0, getattr(self, "step_rc%s" % _d, 100) + 1, 2):
					_v = self._add_sub(self.middle, i, opt) #_o = ("+", "-")
					self.cmd_map["rc"]([_d, _v]) #_d = (1, 2, 3, 4)
					self.time.sleep(self.change_speed)
					setattr(self, "now_rc%s" % _o, _v)
				if _time != 0:
					self.time.sleep(_time if _time else self.keep_time)
					self._set_middle(_d)
	def _add_sub(self, num1, num2, opt):
		if opt == "+":
			return num1 + num2
		elif opt == "-":
			return num1 - num2
		else:
			raise ValueError



	


	#@_wait_until_notbusy
	def _set_middle(self, channel):
		if not self.status.manual_control:
			channel_raw = getattr(self, "now_rc%s" % channel, self.middle)
			print(channel_raw)
			while abs(channel_raw - self.middle) > 2:
				if channel_raw > self.middle:
					channel_raw -= 2 
				else:
					channel_raw += 2
				self.cmd_map["rc"]([channel, str(channel_raw)])
				print("%-5s : %-5s : %-5s" % (channel, channel_raw, self.middle))
				self.time.sleep(self.change_speed)
			self.cmd_map["rc"]([channel, self.middle])
				##channel_raw = int(self.status.status["RC_CHANNELS_RAW"]["chan%s_raw" % channel])

	def auto_fly(self):
		#('front', 'rear', 'left', 'right')
		while 1:
			if self.status.left < self.left_min:
				self.move_right()
			if self.status.right < self.right_min:
				self.move_left()
			if self.status.started_clean:
				if self.status.front < self.front_max:
					self.move_front()
			else:
				if self.status.rear < self.rear_min:
					self.move_rear()
				if self.status.front < self.front_min:
					self.move_front()

	def update_mpstate_status(self, sonar):
		#sonar = self.sensor_control.Sonar()
		while 1:
		# update the stauts of mpstate, GPS raw, hight, direction
		# distance of for direction, front, rear, left, right
			
			self.status.left = sonar.measure('left')
			time.sleep(0.1)
			self.status.right = sonar.measure('right')
			time.sleep(0.1)
			self.status.rear = sonar.measure('rear')
			time.sleep(0.1)
			self.status.front = sonar.measure('front')
			if self.status.front < 1:
				self.status.started_clean = 1
			else:
				self.status.started_clean = 0
			# time.sleep(0.1)
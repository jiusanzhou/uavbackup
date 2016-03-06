#!/usr/bin/env python
'''
Data

'''
import time

# class CommandsHeartBeat(object):
# 	"""docstring for CommandsHeartBeat"""
# 	def __init__(self, input_queue):
# 		super(CommandsHeartBeat, self).__init__()
# 		self.input_queue = input_queue
# 	def send_heart(self):
# 		pass

class SocketIOConsole(object):
	"""docstring for SocketIOConsole"""
	def __init__(self, socketIO, status, addr=("127.0.0.1", 3333)):
		super(SocketIOConsole, self).__init__()
		self.socketIO = socketIO
		self.status = status

	def write(self, msg, bg="MAV", fg=""):		
		if len(msg) > 1:
			try:
				self.socketIO.emit('log message', msg+"^"+self.status.flightmode)
			except:
				pass

	def writeln(self, msg, bg="MAV", fg=""):
		if len(msg) > 1:
			try:
				self.socketIO.emit('log message', msg+"^"+self.status.flightmode)
			except:
				pass

class ServerConsole(object):
	"""docstring for ServerConsole"""
	def __init__(self, status, input_queue, addr=("127.0.0.1", 33333)):
		super(ServerConsole, self).__init__()
		self.status = status
		self.input_queue = input_queue
		self.heart_flag = "*"
		import socket
		try:
			self.udpserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		except socket.error:
			print 'Failed to create socket'
			sys.exit()
		if isinstance(addr, tuple):
			self.addr = addr



	def write(self, msg, bg="MAV", fg=""):
		if len(msg) > 1:
			try:
				self.udpserver.sendto(msg+"^"+self.status.flightmode, self.addr)
			except Exception, e:
				pass
	def writeln(self, msg, bg="MAV", fg=""):
		if len(msg) > 1:
			try:
				self.udpserver.sendto(msg+"^"+self.status.flightmode, self.addr)
			except Exception, e:
				pass
	def send_heart(self, data=None):
		# d = str(data) if data else self.heart_flag
		d = str(data) if data else self.heart_flag
		self.udpserver.sendto(d, self.addr)
		recv_data, addr = self.udpserver.recvfrom(256)
		if len(str(recv_data)) != 1:
			self.input_queue.put(str(recv_data))
			print("%-15s : %s" % (time.time(), str(recv_data)))

class Status(object):
	"""docstring for Status"""
	def __init__(self, msgs):
		super(Status, self).__init__()
		self.msgs = msgs

	def update(self):
		pass

	def get_data(self, name1, name2):
		if name1 and name2:
			try:
				_v1 = self.msgs.get(name1, '')
				_v2 = re.compile('%s : (\d+)' % name2).findall(str(_v1))[0]
			except Exception, e:
				_v2 = ""
			return _v2
		else:
			res = {}
			for key in self.msgs.keys():
				_r = {}
				_v = str(self.msgs[key]).split(", ")
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
		

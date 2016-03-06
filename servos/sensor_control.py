#!/usr/bin/env python
#coding=utf-8

import Adafruit_BBIO.GPIO as GPIO
import time, signal

'''
Getting the sensor data

'''

class sonar(object):	
	"""docstring for Sonnar"""
	ahead = ("GPIO1_13", "GPIO1_12")
	back = ("GPIO1_15", "GPIO1_14")
	#left = ("", "")
	#right = ("", "")

	def __init__(self, **kw):
		super(Sonnar, self).__init__()

		for i in kw:
			setattr(self, i, kw[i])

	def dis_ahead(self):
		return self.distance(self.ahead)

	def dis_back(self):
		return self.distance(self.back)

	def dis_ch(self,direction):
		return self.distance(getattr(self,direction,self.ahead))
  	
	def _overtime(self, signum, frame):
		raise AssertionError
	
	def _distance_one(self, pins):
		GPIO.output(pins[0], GPIO.HIGH)
		time.sleep(0.00015)
		GPIO.output(pins[0], GPIO.LOW)

		while not GPIO.input((pins[1]):
			pass

		st = time.time()

		while GPIO.input((pins[1]):
		#et = time.time()
		#if ((et-st)>outtime):
		#  print("Too long...")
		#   toflag = 1
		#  break
		#print("Heigh")
			pass
		et = time.time()
		return (et - st)*340/2

	def distance(self, pins, times=5, outtime=1):
		GPIO.setup(pins[0], GPIO.OUT)
		GPIO.setup(pins[1], GPIO.IN)
		res = []
		while(len(res)<times):
			#print(len(res))
			try:
				signal.signal(signal.SIGALRM, _overtime)
				signal.alarm(outtime)
				dis = self._distance_one(pins)
				signal.alarm(0)
			except:
				dis = 0
			if dis:
				res.append(dis)
		res.sort()

		GPIO.clearup()
		return (res[1]+res[2]+res[3])/3



if __name__=='__main__':

	while 1
		raw_input("Press ENTER to measure!")
			s = sonar()
			distance = s.dis_ahead()			
			print(distance)
			#print("distance is :%d",distance )





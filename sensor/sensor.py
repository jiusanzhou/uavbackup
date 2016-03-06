#!/usr/bin/env python
#coding=utf-8
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import time, signal

'''
Getting the sensor data

'''

class Sonar(object):
  """docstring for Sonnar"""

  front = ("P8_7", "P8_8", "P8_13")
  rear = ("P8_9", "P8_10", "")
  left = ("P8_11", "P8_12", "")
  right = ("P8_15", "P8_16", "")

  velocityofsound = 340

  def __init__(self, **kwargs):
    super(Sonar, self).__init__()
    self.kwargs = kwargs
    for i in kwargs:
      if isinstance(i, tuple):
        GPIO.setup(_x[0], GPIO.OUT)
        GPIO.setup(_x[1], GPIO.IN)
        if _x[2]:
          PWM.start(_x[2], 8.333, 50, 0) # The dirty duty setted to 8.333 is for 90 deg.
      setattr(self, i, kwargs[i])

    for x in ["front", "rear", "left", "right"]:
      _x = getattr(self, x, None)
      if _x:
        GPIO.setup(_x[0], GPIO.OUT)
        GPIO.setup(_x[1], GPIO.IN)
        if _x[2]:
          PWM.start(_x[2], 8.333, 50, 0)

    self.velocityofsound = self.velocityofsound if 335 < self.velocityofsound < 345 else 340
  def measure(self, direction, angle = 0, overtime = 1, times = 5, maxovertime = 0):

    maxovertime = maxovertime if maxovertime else times * 1
    if isinstance(direction, str):
      direction = getattr(self, direction, None)
    elif isinstance(direction, tuple):
      GPIO.setup(direction[0], GPIO.OUT)
      GPIO.setup(direction[1], GPIO.IN)
    else:
      raise ValueError
      print("Pins error!")
      return
    if direction:
      if angle:
        try:
          PWM.set_duty_cycle(direction[3], (angle + 150) / 18.0)
        except Exception, e:
          raise e
      r = self._sonar(direction[0], direction[1], times, overtime, maxovertime)
      return r
    else:
      raise ValueError
      print("No direction!")
      return
  def _sonar(self, trig, echo, times, overtime, maxovertime):

    _res = []
    _hadovertime = 0

    def _overtime(r, f):
      raise AssertionError

    while (len(_res) < times) and (_hadovertime < maxovertime):
      try:
        signal.signal(signal.SIGALRM, _overtime)
        signal.alarm(overtime)
        _dis = self._sonar_once(trig, echo)
        signal.alarm(0)
      except AssertionError:
        _dis = 0
        _hadovertime += 1
      if _dis:
        _res.append(_dis)
    _lenofres = len(_res)
    #GPIO.cleanup()
    if _lenofres == 0:
        #print("No result!")
        return
    elif _lenofres < 3:
      return sum(_res) / _lenofres
    else:
      return  sum(_res[1:-1]) / (_lenofres - 2)
  def _sonar_once(self, trig, echo):

    GPIO.output(trig, GPIO.HIGH)
    time.sleep(0.00015)
    GPIO.output(trig, GPIO.LOW)

    while not GPIO.input(echo):
      pass
    _st = time.time()

    while GPIO.input(echo):
      pass
    _et = time.time()
    return (_et - _st) * self.velocityofsound / 2

  def _servo(self, pin, angle):
    pass

if __name__ == '__main__':
  s = Sonar()
  while 1:
    raw_input("Please ENTER:")
    for x in ["front", "rear", "left", "right"]:
      st = time.time()
      rx = s.measure(x, times=3)
      et = time.time()
      print("%-10s : %-20s - %s" % (x, rx, (et - st)))

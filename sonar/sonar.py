#coding=utf-8
import Adafruit_BBIO.GPIO as GPIO
import time, signal

Tr = "P8_9"
Eh = "P8_10"
overtimetimes = 0

def Overtime(signum, frame):
  raise AssertionError
  #overtimetimes += 1

def SonarOne():

  GPIO.output(Tr, GPIO.HIGH)
  time.sleep(0.00015)
  GPIO.output(Tr, GPIO.LOW)

  while not GPIO.input(Eh):
    #st = time.time()
    #print("Low")
    pass
  st = time.time()

  while GPIO.input(Eh):
    #et = time.time()
    #if ((et-st)>outtime):
    #  print("Too long...")
    #   toflag = 1
    #  break
    #print("Heigh")
    pass
  et = time.time()
  return (et - st)*340/2

def Sonar(times=5, outtime=1):
  res = []
  global overtimetimes
  while (len(res)<times) and (overtimetimes < 5):
    print(len(res))
    try:
      signal.signal(signal.SIGALRM, Overtime)
      signal.alarm(outtime)
      dis = SonarOne()
      signal.alarm(0)
    except:
      overtimetimes += 1
      dis = 0
    if dis:
      res.append(dis)
  if not len(res):
    print("Over max error times...")
    return
  res.sort()
  return (res[1]+res[2]+res[3])/3

while 1:
  GPIO.setup(Tr, GPIO.OUT)
  GPIO.setup(Eh, GPIO.IN)
  raw_input("Press ENTER to measure!")
  overtimetimes = 0
  print("Trig on :"+Tr+"\nEcho on: "+Eh)
  #try:
  #  signal.signal(signal.SIGALRM, Overtime)
  #  signal.alarm(1)
  #  m = SonarOne()
  #  signal.alarm(0)
  #  print("The distance is %s m"%m)
  #except:
  #  print("Time out...")
  print("Measure is %s m"%Sonar())
  GPIO.cleanup()

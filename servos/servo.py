#coding=utf-8
import Adafruit_BBIO.PWM as PWM
import time

NOWVALUE = 0.5

def left(p):
  global NOWVALUE
  if NOWVALUE>2.5:
    NOWVALUE -= 0.1
    PWM.set_duty_cycle(p, NOWVALUE)
  #else:
  #  print("Cann't left more!")

def right(p):
  global NOWVALUE
  if NOWVALUE<12.5:
    NOWVALUE += 0.1
    PWM.set_duty_cycle(p, NOWVALUE)
  #else:
  #  print("Cann't right more!")

def main():
  pin = "P9_14"
  PWM.start(pin, 7.5, 50, 1)
  keys_map = {"l": left, "r": right}
  while 1:
    left(pin)
    right(pin)
    time.sleep(1)

if __name__ == "__main__":
  main()


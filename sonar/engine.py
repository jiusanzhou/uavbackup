#!/usr/bin/env python
#coding=utf-8

import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import time, signal

#PWM.start(channel, duty, freq=2000, polarity=0)
#PWM.set_duty_cycle("P9_14", 25.5)
#PWM.set_frequency("P9_14", 10)


# def engine_left():
#     for i in range(101):
#         PWM.set_duty_cycle("P9_14", i)
#         time.sleep(0.01)

# def engine_right():
#     for i in range(101):
#         PWM.set_duty_cycle("P9_14", 100 - i)
#         time.sleep(0.01)

def engine(angle):
    #PWM.set_duty_cycle("P9_14", (angle/36)+5)
    if angle < 0:
        angle = 0
    elif angle > 180:
        angle = 180
    PWM.set_duty_cycle("P9_14", (angle+60)/18)

if __name__=='__main__':

    PWM.start("P9_14", 13.3, 50, 0)
    #raw_input("Press ENTER to measure!")
    while 1:
        angle_num = input('Please input  the angle:')
        angle_num = float(angle_num)
        engine(angle_num)
        # PWM.stop("P9_14")
        # PWM.cleanup()

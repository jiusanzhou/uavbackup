import Adafruit_BBIO.PWM as PWM
import time

def main():
    print("Start, the speed is the Highest")
    pin = "P9_14"
    PWM.start(pin, 50)
    setSpeed(pin, 1)
    raw_input("Input enter to start")
    setSpeed(pin, 0)
    raw_input("Input enter to continue")
    setSpeed(pin, 0.1)
    while 1:
        inpt = raw_input("Please input the speed: ")
        if 0<=inpt<=1:
            setSpeed(pin, inpt)
def setSpeed(pin, speed=0.5):
    if pin and 0<=speed<=1:
        PWM.set_frequency(pin, 1000/(1+speed))
        PWM.set_duty_cycle(pin, 0.7)#(0.7+speed)/(1+speed))
        print("The speed is setted to %s"%speed)

if __name__ == "__main__":
    main()

# #!/usr/bin/env python
# #coding=utf-8

# import Adafruit_BBIO.GPIO as GPIO
# import time, signal

# '''
# Getting the sensor data
# '''     
# class sonar(object):    
#     """docstring for Sonnar"""
#     ahead = ('GPIO1_13', 'GPIO1_12')
#     back = ('GPIO1_15', 'GPIO1_14')
#     #left = ("", "")
#     #right = ("", "")

#     def __init__(self, **kw):
#         #super(sonar, self).__init__()
#         for i in kw:
#             setattr(self, i, kw[i])
                     
#     def dis_ahead(self):
#         print('dis_ahead_init')
#         return self.distance(self.ahead)

#     def dis_back(self):
#         return self.distance(self.back)

#     def dis_ch(self,direction):
#         return self.distance(getattr(self,direction,self.ahead))
    
#     def overtime(self, signum, frame):
#         print('overtime')
#         raise AssertionError
    
#     def _distance_one(self, pins):
#         c = pins
#         GPIO.output("GPIO1_13", GPIO.HIGH)
#         time.sleep(0.00015)
#         GPIO.output("GPIO1_13", GPIO.LOW)
#         print('_distance_one_be_used')

#         while not GPIO.input("GPIO1_12"):
#             pass
#         #print('start_time = %d',time.time())
#         st = time.time()

#         while GPIO.input("GPIO1_12"):
#         #et = time.time()
#         #if ((et-st)>outtime):
#         #  print("Too long...")
#         #   toflag = 1
#         #  break
#         #print("Heigh")
#             pass
#         #print('end_time')
#         et = time.time()
#         print('return_et-st')
#         return (et - st)*340/2

#     def distance(self, pins, times=5, outtime=1):
#         #GPIO.setup(pins[0], GPIO.OUT)
#         #GPIO.setup(pins[1], GPIO.IN)
#         print('GPIO_init')
#         res = []
#         while(len(res)<times):
#             #print(len(res))
#             #try:
#             signal.signal(signal.SIGALRM, self.overtime)
#             signal.alarm(outtime)
#             print('signal_alarm')
#             dis = self._distance_one(pins)
#             signal.alarm(0)
#             #except:
#             #dis = 0
#             if dis:
#                 res.append(dis)
#                 print('get_one_num')
#         res.sort()

#         #GPIO.clearup()
        
#         return (res[1]+res[2]+res[3])/3


# if __name__=='__main__':

#     while 1:
#         GPIO.setup("GPIO1_13", GPIO.OUT)
#         GPIO.setup("GPIO1_12", GPIO.IN)
#         raw_input("Press ENTER to measure!")
#         s = sonar()
#         distance = s.dis_ahead()            
#         print(distance)

#         ss = sonar()
#         ddistance = ss.distance(('GPIO1_13', 'GPIO1_12'))
#         #print("distance is :%d",distance )

#         GPIO.clearup()


#coding=utf-8
import Adafruit_BBIO.GPIO as GPIO
import time, signal

class sonar(object):
    def __init__(self, **kw):
        self.Tr = "GPIO1_13"
        self.Eh = "GPIO1_12"
        self.ahead = ('GPIO1_13', 'GPIO1_12')
        self.back=('GPIO1_15', 'GPIO1_14')
        for i in kw:
            setattr(self, i, kw[i])


    def overtime(self,signum, frame):
        raise AssertionError

    def dis_ahead(self):
        return self.distance(self.ahead)

    def dis_back(self):
        return self.distance(self.back)

    # def dis_ch(self,direction):
    #     return self.distance(getattr(self,direction,self.ahead))

    def distance_one(self,pins):
        # GPIO.output(self.Tr, GPIO.HIGH)
        # time.sleep(0.00015)
        # GPIO.output(self.Tr, GPIO.LOW)

        GPIO.output(pins[0], GPIO.HIGH)
        time.sleep(0.00015)
        GPIO.output(pins[0], GPIO.LOW)
        print('SonarOne_test')

        #while not GPIO.input(self.Eh):
        while not GPIO.input(pins[1]):
            pass
        st = time.time()

        #while GPIO.input(self.Eh):
        while GPIO.input(pins[1]):
            pass
        et = time.time()
        return (et - st)*340/2

    def distance(self,pins,times=5, outtime=2):
        res = []
        while(len(res)<times):
            try:
                signal.signal(signal.SIGALRM, self.overtime)
                signal.alarm(outtime)
                dis = self.distance_one(pins)
                signal.alarm(0)
            except:
                dis = 0

            if dis:
                res.append(dis)

        res.sort()
        return (res[1]+res[2]+res[3])/3

if __name__=='__main__':
    while 1:
        GPIO.setup('GPIO1_13', GPIO.OUT)
        GPIO.setup('GPIO1_12', GPIO.IN)
        pin = ('GPIO1_13','GPIO1_12')
        raw_input("Press ENTER to measure!")
        s = sonar()
        d = s.distance(pin)
        print("distance is : %s m" %d)

        GPIO.cleanup()


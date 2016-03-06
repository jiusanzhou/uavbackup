import cv2, time
import cv2.cv as cv

def main():
  camera = cv2.VideoCapture(0)#cv.CaptureFromCAM(0)#058f:3823)
  time.sleep(0.5)
  #while 1:
  (grabbed, frame) = camera.read()
  #cv2.imshow("WebcamTest", frame)
  print(type(frame))
  cv.WaitKey(0)
  cv.SaveImage("/root/1.jpg", frame)
  
if __name__ == "__main__":
  main()


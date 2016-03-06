import cv2.cv as cv
import random

im = cv.LoadImage('meinv.jpg')
thumb = cv.CreateImage((im.width / 2, im.height / 2), cv.CV_8UC2, 3)
cv.Resize(im, thumb)

for k in range(5000):
    i = random.randint(0, thumb.height-1)
    j = random.randint(0, thumb.width-1)
    color = (random.randrange(256), random.randrange(256), random.randrange(256))

    thumb[i, j] = color

li = cv.InitLineIterator(thumb, (0, 0), (10, 10))

for (r, g, b) in li:
    print (r, g, b)

cv.ShowImage("Noize", thumb)
cv.WaitKey(0)

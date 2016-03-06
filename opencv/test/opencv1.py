#coding=utf-8

import cv2.cv as cv

image = cv.LoadImage('meinv.jpg', cv.CV_LOAD_IMAGE_COLOR)

font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1, 1, 0, 3, 8)
y = image.height / 4
x = image.width / 2

cv.PutText(image, "Hello Meinv!", (x, y), font, cv.RGB(0, 0, 0))

thumb = cv.CreateImage((image.width / 2, image.height / 2), cv.CV_8UC2, 3)
cv.Resize(image, thumb)
#cvt = cv.CreateImage(cv.GetSize(thumb), cv.CV_8UC2, 3)
#cv.CvtColor(thumb, cvt, cv.CV_RGB2BGR)
#cv.NamedWindow('Image', cv.CV_WINDOW_AUTOSIZE)

b = cv.CreateImage(cv.GetSize(thumb), thumb.depth, 1)
g = cv.CloneImage(b)
r = cv.CloneImage(b)

cv.Split(thumb, b, g, r, None)

merged = cv.CreateImage(cv.GetSize(thumb), 8, 3)
cv.Merge(g, b, r, None, merged)


cv.ShowImage('Image', thumb)
cv.ShowImage('Blue', b)
cv.ShowImage('Green', g)
cv.ShowImage('Red', r)
cv.ShowImage('Merged', merged)
cv.WaitKey(0)

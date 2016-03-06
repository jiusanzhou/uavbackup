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

grey = cv.CreateImage(cv.GetSize(thumb), 8, 1)
cv.CvtColor(thumb, grey, cv.CV_RGB2GRAY)
cv.ShowImage('Greyed', grey)

smoothed = cv.CloneImage(thumb)
cv.Smooth(thumb, smoothed, cv.CV_MEDIAN)
cv.ShowImage('Smoothed', smoothed)

cv.EqualizeHist(grey, grey)
cv.ShowImage('Equalized', grey)

threshold1 = cv.CloneImage(grey)
cv.Threshold(threshold1, threshold1, 100, 255, cv.CV_THRESH_BINARY)
cv.ShowImage('Threshold1', threshold1)

threshold2 = cv.CloneImage(grey)
cv.Threshold(threshold2, threshold2, 100, 255, cv.CV_THRESH_OTSU)
cv.ShowImage('Threshold2', threshold2)

element_shape = cv.CV_SHAPE_RECT
pos = 3
element = cv.CreateStructuringElementEx(pos*2+1, pos*2+1, pos, pos, element_shape)
cv.Dilate(grey, grey, element, 2)

cv.ShowImage('Dilated', grey)
cv.WaitKey(0)

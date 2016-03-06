import cv2.cv as cv

im = cv.LoadImage("meinv.jpg", cv.CV_8U)

cv.SetImageROI(im, (1, 1,30,30))

histsize = 256 #Because we are working on grayscale pictures
hist = cv.CreateHist([histsize], cv.CV_HIST_ARRAY, [[0,histsize]], 1)
cv.CalcHist([im], hist)


cv.NormalizeHist(hist,1) # The factor rescale values by multiplying values by the factor
_,max_value,_,_ = cv.GetMinMaxHistValue(hist)

if max_value == 0:
    max_value = 1.0
cv.NormalizeHist(hist,256/max_value)

cv.ResetImageROI(im)

res = cv.CreateMat(im.height, im.width, cv.CV_8U)
cv.CalcBackProject([im], res, hist)

cv.Rectangle(im, (1,1), (30,30), (0,0,255), 2, cv.CV_FILLED)
cv.ShowImage("Original Image", im)
cv.ShowImage("BackProjected", res)
cv.WaitKey(0)

import numpy as np
import urllib
import cv2

urls = [ 
    "http://g.hiphotos.baidu.com/image/pic/item/503d269759ee3d6debd5c6c141166d224f4adead.jpg",
    "http://e.hiphotos.baidu.com/image/pic/item/622762d0f703918f9c4af8c7533d269759eec420.jpg",
]

def url_to_image(url):
    resp = urllib.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.COLOR_BAYER_BG2BGR)
    return image

def find_marker(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 35, 125)
    return edged
    #(cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    #c = max(cnts, key = cv2.contourArea)
    #return cv2.minAreaRect(c)

for url in urls:
    print("Download %s" % url)
    image = find_marker(url_to_image(url))
    cv2.imshow("Image", image)
    cv2.waitKey(0)

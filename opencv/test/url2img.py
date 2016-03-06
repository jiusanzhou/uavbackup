import numpy as np
import urllib
import cv2

def url_to_image(url):
    resp = urllib.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.COLOR_BAYER_BG2BGR)
    return image

urls = [
        "http://www.pyimagesearch.com/wp-content/uploads/2015/01/opencv_logo.png",
        "http://www.pyimagesearch.com/wp-content/uploads/2015/01/google_logo.png",
        "http://www.pyimagesearch.com/wp-content/uploads/2014/12/adrian_face_detection_sidebar.png"
    ]

for url in urls:
    print("Download %s" % url)
    image = url_to_image(url)
    cv2.imshow("Image", image)
    cv2.waitKey(0)

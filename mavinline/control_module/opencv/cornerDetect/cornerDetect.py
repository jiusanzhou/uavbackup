import cv2

def main():
    cap = cv2.VideoCapture(0)
    suc, frm = cap.read()
    while suc:
        
        cv2.imshow("test", new_frm)
        cv2.waitKey(0)
        cv2.destroyWindow("test")

if __name__ == '__main__':
    main()


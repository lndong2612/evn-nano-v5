"""Access IP Camera in Python OpenCV"""
import os
import cv2

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"
# replace with your ip address
USER = 'admin'
PASSWORD = 'CHBAJT'
IPADDRESS = '10.10.10.100'
PORT = '554'

url = f'rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/onvif1'
cap = cv2.VideoCapture(url)

while True:
    ret, img = cap.read()
    if ret == True:
        
        cv2.imshow('video output', cv2.resize(img,(1080, 720)))
        if cv2.waitKey(1) &0XFF == ord('q'):
            break    

cap.release()
cv2.destroyAllWindows()


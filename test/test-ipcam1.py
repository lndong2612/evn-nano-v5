"""Access IP Camera in Python OpenCV"""
import os
import cv2
import time
USER = 'admin'
PASSWORD = 'thinklabs@36'
IPADDRESS = '10.10.10.29'
PORT = '554'
#url = f"rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/h264Preview_01_main"
url = f'rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/onvif1'
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = 'rtsp_transport;udp'
# replace with your ip address
# USER = 'admin'
# PASSWORD = 'CHBAJT'
# IPADDRESS = '10.10.10.100'
# PORT = '554'
# url = f'rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/onvif1'



cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
while True:
    ret, img = cap.read()
    print(img.shape)
    if ret == True:
        cv2.imshow('Camera', img)
        if cv2.waitKey(1) &0XFF == ord('q'):
            break    

cap.release()
cv2.destroyAllWindows()


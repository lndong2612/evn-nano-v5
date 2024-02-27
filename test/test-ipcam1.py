"""Access IP Camera in Python OpenCV"""
import os
import cv2
import time
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"
# replace with your ip address
# USER = 'admin'
# PASSWORD = 'CHBAJT'
# IPADDRESS = '10.10.10.100'
# PORT = '554'
# url = f'rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/onvif1'

USER = 'admin'
PASSWORD = 'thinklabs@36'
IPADDRESS = '10.10.10.29'
PORT = '554'
url = f"rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/cam/realmonitor?channel=1&subtype=1"

cap = cv2.VideoCapture(url)
start_time = time.time()
# FPS update time in seconds
display_time = 2
fc = 0
FPS = 0
# font which we will be using to display FPS 
font = cv2.FONT_HERSHEY_SIMPLEX 
while True:
    ret, img = cap.read()
    if ret == True:
        fc+=1
        TIME = time.time() - start_time

        if (TIME) >= display_time :
            FPS = fc / (TIME)
            fc = 0
            start_time = time.time()

        fps_disp = "FPS: "+str(FPS)[:5]
        # putting the FPS count on the frame 
        cv2.putText(img, fps_disp, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA) 
        cv2.imshow('video output', cv2.resize(img,(1080, 720)))
        if cv2.waitKey(1) &0XFF == ord('q'):
            break    

cap.release()
cv2.destroyAllWindows()


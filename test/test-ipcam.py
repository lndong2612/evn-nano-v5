"""Access IP Camera in Python OpenCV"""
import os
import cv2
import time
from imutils.video import VideoStream
USER = 'admin'
PASSWORD = 'CHBAJT'
IPADDRESS = '10.10.10.36'
PORT = '554'
#url = f"rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/h264Preview_01_main"
# url = f'rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/onvif1'
url = 'rtsp://admin:thinklabs@36@10.10.10.29:554/Streaming/Channels/101'
# url = f'rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/cam/realmonitor?channel=1&subtype=1' # camera Dahua
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = 'rtsp_transport;udp'
# replace with your ip address
# USER = 'admin'
# PASSWORD = 'CHBAJT'
# IPADDRESS = '10.10.10.100'
# PORT = '554'
# url = f'rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/onvif1'

cap = VideoStream(url).start()   
while True:
    img = cap.read()
    cv2.imshow('Camera', img)
    if cv2.waitKey(1) &0XFF == ord('q'):
       break

cap.stop()
cv2.destroyAllWindows()


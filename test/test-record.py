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
url = f'rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/onvif1'
# url = f'rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/cam/realmonitor?channel=1&subtype=1' # camera Dahua
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = 'rtsp_transport;udp'
# replace with your ip address
# USER = 'admin'
# PASSWORD = 'CHBAJT'
# IPADDRESS = '10.10.10.100'
# PORT = '554'
# url = f'rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/onvif1'
# Define the codec (XVID) and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')


cap = VideoStream(url).start()
img = cap.read()
h = img.shape[0]
w = img.shape[1]
cap1 = cv2.VideoCapture(url)
# fps = cap1.get(cv2.CAP_PROP_FPS)
# print(fps)
out = cv2.VideoWriter('output.mp4', fourcc, 30, (w, h))
while True:
    img = cap.read()
    cv2.imshow('Camera', img)
    out.write(img)  # Write the frame to the output video
    if cv2.waitKey(1) &0XFF == ord('q'):
       break

cap.stop()
cv2.destroyAllWindows()


"""Access IP Camera in Python OpenCV"""
import os
import cv2
import time
from imutils.video import VideoStream
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



#cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
cap = VideoStream(url).start()
#while True:
 #   ret, img = cap.read()
  #  print(img.shape)
   # if ret == True:
    #    cv2.imshow('Camera', img)
     #   if cv2.waitKey(1) &0XFF == ord('q'):
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (1920, 1080)) 
      #      break    
while True:
    img = cap.read()
    out.write(img)  
    #cv2.imshow('Camera', img)
    #if cv2.waitKey(1) &0XFF == ord('q'):
    #    break  
cap.stop()
cv2.destroyAllWindows()


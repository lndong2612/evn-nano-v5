"""Access IP Camera in Python OpenCV"""
import os
import cv2
import time
from imutils.video import VideoStream
# # INFO camera

'''Camera Ezviz'''
# # ---------------------------------------------------------------
# USER = 'admin'
# PASSWORD = 'CHBAJT'
# IPADDRESS = '10.10.10.100'
# PORT = '554'
# URL = f'rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/onvif1'
# # ---------------------------------------------------------------


'''Camera Dahua'''
# # ---------------------------------------------------------------
# USER = 'admin'
# PASSWORD = 'abcd1234'
# IPADDRESS = '10.10.10.100'
# PORT = '554'
# URL = f"rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/cam/realmonitor?channel=1&subtype=1"
# # ---------------------------------------------------------------


'''Camera HIK'''
# # ---------------------------------------------------------------
USER = 'admin'
PASSWORD = 'thinklabs@36'
IPADDRESS = '10.10.10.29'
PORT = '554'
URL = f"rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/ISAPI/Streaming/channels/101"
# # ---------------------------------------------------------------


def camera(recall):
    while (recall):
        ret, img = cap.read()
        cv2.imshow('video output', cv2.resize(img,(1080, 720)))
        if cv2.waitKey(1) &0XFF == ord('q'):
            break    

    cap.release()
    cv2.destroyAllWindows()

cap = VideoStream(URL).start()

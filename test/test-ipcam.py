"""Access IP Camera in Python OpenCV"""
import os
import cv2
import json
from imutils.video import VideoStream

with open(os.path.join(os.getcwd(), 'info.json'), "r") as outfile:
    info_json = json.load(outfile)
    IPCAM = info_json['ip_camera']
    IPEDGECOM = info_json['ip_edgecom']
    USERCAM = info_json['user_camera']
    PASSWORDCAM = info_json['password_camera']
    PORTCAM = info_json['port_camera']
    RTSP_FORMAT = info_json['rtsp_format']
URL = f'rtsp://{USERCAM}:{PASSWORDCAM}@{IPCAM}:{PORTCAM}/{RTSP_FORMAT}'

# URL = f'rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/onvif1'
# URL = f'rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/cam/realmonitor?channel=1&subtype=1' # camera Dahua
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = 'rtsp_transport;udp'

cap = VideoStream(URL).start()
while True:
    img = cap.read()
    cv2.imshow('Camera', img)
    if cv2.waitKey(1) &0XFF == ord('q'):
       break

cap.stop()
cv2.destroyAllWindows()


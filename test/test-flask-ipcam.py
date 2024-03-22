"""Access IP Camera in Python OpenCV"""
import os
import sys
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))
import cv2
import time
import signal
from flask import Flask, Response, jsonify
from utils.function import VideoStream
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"


'''------------------------------------------------------------------------------------'''
# replace with your ip address
USER = 'admin'
PASSWORD = 'thinklabs@36'
IPADDRESS = '10.10.10.29'
PORT = '554'
RTSP_FORMAT = 'Streaming/Channels/101'
URL = f"rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/{RTSP_FORMAT}"

# HIK
# Streaming/Channels/101

# Dahua
# cam/realmonitor?channel=1&subtype=1

# Ezviz
# onvif1
'''------------------------------------------------------------------------------------'''


app = Flask(__name__)


cap = VideoStream(URL).start()

@app.route('/')
def index():
    return '[INFO] Running ...'


def generate_resize():
    while True:
        '''Read the camera resize frame'''
        (grabbed, frame_resize) = cap.read()
        frame_resize_output = cv2.resize(frame_resize, (853, 480))
        (flag, encodedImage) = cv2.imencode(".jpg", frame_resize_output)
        # ensure the frame was successfully encoded
        if not flag:
            continue
        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')


def handler():
    res = input("[INFO] Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y' or res == 'Y':
        exit(0)


@app.route("/api/video_feed_resize")
def video_feed_resize():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate_resize(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")
 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='9298', debug=False)    


# release the video stream pointer
signal.signal(signal.SIGINT, handler)

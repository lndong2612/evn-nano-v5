"""Access IP Camera in Python OpenCV"""
import os
import cv2
import time
import signal
from flask import Flask, Response, jsonify
from imutils.video import VideoStream
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"
# replace with your ip address
# USER = 'admin'
# PASSWORD = 'CHBAJT'
# IPADDRESS = '10.10.10.36'
# PORT = '554'
# URL = f'rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/onvif1'

USER = 'admin'
PASSWORD = 'thinklabs@36'
IPADDRESS = '10.10.10.29'
PORT = '554'
URL = f"rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/cam/realmonitor?channel=1&subtype=1"

app = Flask(__name__)

while(True):
    cap = VideoStream(URL).start()
    frame = cap.read()
    try:
        height = frame.shape[0]    
        print('[INFO] Connect camera done!!')
        break
    except:
        time.sleep(5)
        print('[INFO] Connect camera again ...')
        continue

# frame = cap.read()
height = frame.shape[0]
width = frame.shape[1]

@app.route('/')
def index():
    return '[INFO] Running ...'


def generate():
    cap = VideoStream(URL).start()
    try:
        while True:
            ''' Read the camera frame'''
            frame = cap.read()
            (flag, encodedImage) = cv2.imencode(".jpg", frame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
            # yield the output frame in the byte format
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                bytearray(encodedImage) + b'\r\n')
    except Exception:
        ''' Read the camera frame'''
        frame = cv2.imread('./resources/background/connection-lost.jpg')
        frame = cv2.resize(frame, (width, height))
        (_, encodedImage) = cv2.imencode(".jpg", frame)

        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')


def generate_resize():
    cap = VideoStream(URL).start()
    try:
        while True:
            '''Read the camera resize frame'''
            frame = cap.read()
            frame_resize = cv2.resize(frame, (853, 480))
            (flag, encodedImage) = cv2.imencode(".jpg", frame_resize)
            # ensure the frame was successfully encoded
            if not flag:
                continue
            # yield the output frame in the byte format
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                bytearray(encodedImage) + b'\r\n')
    except Exception:
        ''' Read the camera frame'''
        frame = cv2.imread('./resources/background/connection-lost.jpg')
        frame = cv2.resize(frame, (width, height))
        (_, encodedImage) = cv2.imencode(".jpg", frame)

        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')

def handler():
    res = input("[INFO] Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y' or res == 'Y':
        exit(0)

@app.route("/api/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")


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
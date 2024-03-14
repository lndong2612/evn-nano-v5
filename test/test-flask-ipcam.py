"""Access IP Camera in Python OpenCV"""
import os
import cv2
import time
import signal
from flask import Flask, Response, jsonify
from imutils.video import VideoStream
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"
# replace with your ip address
USER = 'admin'
PASSWORD = 'CHBAJT'
IPADDRESS = '10.10.10.36'
PORT = '554'
# URL = f'rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/onvif1'

# USER = 'admin'
# PASSWORD = 'L2A704B1'
# IPADDRESS = '10.10.40.3'
# PORT = '554'
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


def generate(cap_generate):
    try:
        while True:
            ''' Read the camera frame'''
            frame_generate = cap_generate.read()
            (flag, encodedImage) = cv2.imencode(".jpg", frame_generate)
            # ensure the frame was successfully encoded
            if not flag:
                continue
            # yield the output frame in the byte format
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                bytearray(encodedImage) + b'\r\n')
    except Exception:
        ''' Read the camera frame'''
        frame_generate = cv2.imread('./resources/background/nosignal.jpg')
        frame_generate = cv2.resize(frame, (width, height))
        (_, encodedImage) = cv2.imencode(".jpg", frame_generate)

        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')


def generate_resize(cap_resize):
    
    try:
        while True:
            '''Read the camera resize frame'''
            frame_resize = cap_resize.read()
            frame_resize_output = cv2.resize(frame_resize, (853, 480))
            (flag, encodedImage) = cv2.imencode(".jpg", frame_resize_output)
            # ensure the frame was successfully encoded
            if not flag:
                continue
            # yield the output frame in the byte format
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                bytearray(encodedImage) + b'\r\n')
    except Exception:
        ''' Read the camera frame'''
        frame_resize_output = cv2.imread('./resources/background/nosignal.jpg')
        frame_resize_output = cv2.resize(frame_resize_output, (width, height))
        (_, encodedImage) = cv2.imencode(".jpg", frame_resize_output)

        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')

def handler():
    res = input("[INFO] Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y' or res == 'Y':
        exit(0)

@app.route("/api/video_feed")
def video_feed():
    cap_generate = VideoStream(URL).start()
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(cap_generate),
        mimetype = "multipart/x-mixed-replace; boundary=frame")


@app.route("/api/video_feed_resize")
def video_feed_resize():
    cap_resize = VideoStream(URL).start()
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate_resize(cap_resize),
        mimetype = "multipart/x-mixed-replace; boundary=frame")
 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='9298', debug=False)    
    
# release the video stream pointer
signal.signal(signal.SIGINT, handler)
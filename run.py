import os
import sys 
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))
import cv2
import json
import time
import logging
import threading
from config import settings
from imutils.video import VideoStream
from flask import Flask, jsonify, Response, request
from flask_cors import CORS
from utils.function import detect_method, health_check_nano

# [logging config
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s:%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
# logging config]

output_fullsize = None
output_resize = None
lock = threading.Lock()
device = '' # cuda device, i.e. 0 or 0,1,2,3 or cpu

with open(os.path.join(os.getcwd(), 'info.json'), "r") as outfile:
    info_json = json.load(outfile)
    USERCAM = info_json['user_camera']
    PASSWORDCAM = info_json['password_camera']
    IPCAM = info_json['ip_camera']
    PORTCAM = info_json['port_camera']
    CHANNELCAM = info_json['channel_camera']
    CROPRATE = info_json['crop_frame_rate']
    IPEDGECOM = info_json['ip_edgecom']

app = Flask(__name__)
CORS(app)
URL = f'rtsp://{USERCAM}:{PASSWORDCAM}@{IPCAM}:{PORTCAM}/onvif{CHANNELCAM}'
cap = VideoStream(URL).start()

time.sleep(10.0)

@app.route('/')
def index():
    return '[INFO] Running ...'

def detect(info_json):
    global cap, output_fullsize, lock, output_resize

    frame_num = 0
    crop_rate = CROPRATE
    while True:
        frame = cap.read()
        frame_num += 1
        if frame_num % 6000 == 0:
            health_check_nano(IPEDGECOM)
        if frame_num % crop_rate == 0:
           input_frame = frame.copy()
           detect_method(input_frame, info_json, device)

        with lock:
            output_fullsize = frame.copy()
            output_resize = frame.copy()
            output_resize = cv2.resize(output_resize, (853, 480))

def generate():
    # grab global references to the output frame and lock variables
    global output_fullsize, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if output_fullsize is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", output_fullsize)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')

def generate_resize():
    # grab global references to the output frame and lock variables
    global output_resize, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if output_resize is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", output_resize)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')

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

@app.route('/api/download_model', methods=['POST'])
def download():
    try:
        file = request.files['file']
        file.save('./resources/weight_init/best.pt') 
        mess = '[INFO] Model saved!'
        return jsonify(status_code = 200, content={'message':mess})
    except SystemError as error:
        mess = '[INFO] Save model fail ...'
        return jsonify(status_code = 400, content={"success":"false", "error": str(error)})

@app.route('/api/reboot', methods = ['GET'])
def reboot():
    try:
        os.system("shutdown -r -t 10")
        mess = '[INFO] System reboot after a few seconds ...'
        return jsonify(status_code = 200, content={'message':mess})
    except SystemError as error:
        mess = '[INFO] System reboot fail ...'
        return jsonify(status_code = 400, content={"success":"false", "error": str(error)})
    exit(0)

if __name__ == "__main__":
    # signal.signal(signal.SIGINT, handler)
    
    # start a thread that will perform object detection
    p1 = threading.Thread(target=detect, args=(info_json,))
    p1.daemon = True
    p1.start()

    host = settings.HOST
    port = int(settings.PORT)
    app.run(host=host, port=port, debug=settings.DEBUG)

# release the video stream pointer
cap.stop()

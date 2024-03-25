import os
import sys
import signal
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))
import cv2
import json
import time
import datetime
import threading
from config import settings
from flask_cors import CORS
from ultralytics import YOLO
from datetime import datetime
from flask import Flask, jsonify, Response, request
from utils.function import (detect_v8, health_check_nano, get_information_from_server , 
                            update_frame_dimension, checking_internet, checking_camera, VideoStream)

''' cuda device, i.e. 0 or 0,1,2,3 or cpu'''
device = '' 


print("[INFO] Run module AI ...")
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
print("[INFO] Date and time computer start: ", dt_string)


'''Auto reboot computer at 5AM '''
print("[INFO] Time to reboot computer ...")
cmd_auto_reboot = 'shutdown -r 18:00'
os.system(cmd_auto_reboot)


'''Wait computer detect sim card'''
print("[INFO] Wait for the sim card to be activated ...")
for i in range(30):
    print(f'Time: {i+1}s')
    time.sleep(1)


'''Open network on sim 4G '''
print("[INFO] Open Sim 4G network ...")
cmd_enable_sim = 'sudo ifmetric wwan0 50'
try:
    os.system(cmd_enable_sim)
    print("[INFO] Done!!")
except Exception as e:
    print("[INFO] Already open!!")
    pass


'''Check internet available or not'''
print("[INFO] Checking internet ...")
checking_internet()


with open(os.path.join(os.getcwd(), 'info.json'), "r") as outfile:
    info_json = json.load(outfile)
    IPCAM = info_json['ip_camera']
    IPEDGECOM = info_json['ip_edgecom']
    USERCAM = info_json['user_camera']
    PASSWORDCAM = info_json['password_camera']
    PORTCAM = info_json['port_camera']
    RTSP_FORMAT = info_json['rtsp_format']

'''Get information from server and update into json file'''
get_information_from_server(IPCAM, IPEDGECOM)


with open(os.path.join(os.getcwd(), 'info.json'), "r") as outfile:
    info_json = json.load(outfile)
    API_NAME = info_json['api_name']

'''Check camera type to get URL'''
URL = f'rtsp://{USERCAM}:{PASSWORDCAM}@{IPCAM}:{PORTCAM}/{RTSP_FORMAT}'
print(f'[INFO] URL Stream: {URL}')


'''Load frame from camera to get H and W'''
print(f'[INFO] Checking connect to camera ...')
_, frame = checking_camera(URL)
height = frame.shape[0]
width = frame.shape[1]
update_frame_dimension(height, width, IPCAM) # Write H and W to json file


'''Load camera'''
print(f'[INFO] Loading camera ...')
cap = VideoStream(URL).start()


'''Load file json about object'''
with open('object.json', 'r', encoding='utf-8') as outfile:
    json_object = json.load(outfile)


app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return '[INFO] Running ...'


'''Detect object on input image'''
def detect(ip_camera):
    conf_thres = settings.CONF_THRES # confidence threshold
    iou_thres = settings.IOU_THRES # NMS IOU threshold
    weight_path = os.path.join(settings.MODEL, 'best.pt')

    """Detect object on input image"""
    model = YOLO(weight_path, "detect")
    imgsz = 640
    stride = 1
    
    while True:
        with open(os.path.join(os.getcwd(), 'info.json'), "r") as outfile:
            info_json = json.load(outfile)
            PTS = info_json['coordinate']
            IDENTIFICATIONTIME = info_json['identification_time']    
        _, frame_detect = cap.read()
        detect_v8(frame_detect, ip_camera, PTS, conf_thres, iou_thres, model, imgsz, stride, json_object)
        time.sleep(IDENTIFICATIONTIME)


'''Send health check camera to server'''
def send_healthcheck(ip_edgecom):
    while True:
        time.sleep(60)
        named_tuple = time.localtime() 
        time_string = time.strftime("%d-%m-%Y %H:%M:%S", named_tuple)
        print(f"[INFO] Health check notification is being sent out on {time_string}.")  
        health_check_nano(ip_edgecom)


'''Read the camera resize frame'''
def generate_resize():
    prev = 0 # Previous frame time
    while True:
        time_elapsed = time.time() - prev
        frame_out_resize = cap.read()
        if time_elapsed > 1./settings.FRAME_RATE:
            prev = time.time()     
            frame_resize = cv2.resize(frame_out_resize, (853, 480))
            (flag, encodedImage) = cv2.imencode(".jpg", frame_resize)
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


@app.route(f"/api/{API_NAME}/video_feed_resize")
def video_feed_resize():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate_resize(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")


@app.route(f'/api/{API_NAME}/download_model', methods=['POST'])
def download():
    try:
        file = request.files['file']
        file.save('./resources/weight_init/best.pt')
        mess = '[INFO] Model saved successfully ✅.'
        os.system("shutdown -r -t 10")
        return jsonify(status_code = 200, content={'message':mess})
    except SystemError as error:
        mess = '[INFO] Model saved fail ❌ ...'
        return jsonify(status_code = 400, content={"success":"false", "error": str(error)})


@app.route(f'/api/{API_NAME}/update_info', methods=['POST'])
def update_info():
    try:
        get_information_from_server(IPCAM, IPEDGECOM)
        mess = '[INFO] Updated information successfully ✅.'
        return jsonify(status_code = 200, content={'message':mess})
    except SystemError as error:
        mess = '[INFO] Updated information fail ❌ ...'
        return jsonify(status_code = 400, content={"success":"false", "error": str(error)})


@app.route(f'/api/{API_NAME}/reboot', methods = ['GET'])
def reboot():
    try:
        os.system("shutdown -r -t 10")
        mess = '[INFO] System reboot after a few seconds ...'
        return jsonify(status_code = 200, content={'message':mess})
    except SystemError as error:
        mess = '[INFO] System reboot fail ...'
        return jsonify(status_code = 400, content={"success":"false", "error": str(error)})


if __name__ == "__main__":
    # Start a thread that will perform object detection, send health check camera and start flask server on Edge computer
    p1 = threading.Thread(target=detect, args=(IPCAM, ))
    p1.daemon = True
    p1.start()

    p2 = threading.Thread(target=send_healthcheck, args=(IPEDGECOM,))
    p2.daemon = True
    p2.start()

    host = settings.HOST
    port = int(settings.PORT)
    app.run(host=host, port=port, debug=False)     
   
    
# release the video stream pointer
signal.signal(signal.SIGINT, handler)
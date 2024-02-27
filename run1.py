import os
import sys 
import signal
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))
import cv2
import json
import time
import threading
from config import settings
from flask_cors import CORS
from datetime import datetime
from imutils.video import VideoStream
from flask import Flask, jsonify, Response, request
from utils.function import (detect_method, health_check_nano, get_information_from_server , 
                            update_frame_dimension, initialize_information_to_server, checking_internet)


print("[INFO] Run module AI ...")
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
print("[INFO] Date and time computer start: ", dt_string)


''' cuda device, i.e. 0 or 0,1,2,3 or cpu'''
device = '' 


time.sleep(30)
'''Open network on sim 4G '''
print("[INFO] Open Sim 4G network ...")
cmd_enable_sim = 'sudo ifmetric wwan0 50'
try:
    os.system(cmd_enable_sim)
    print("[INFO] Done!!")
except Exception as e:
    print("[INFO] Already open!!")
    pass


'''Auto reboot computer at 5AM '''
print("[INFO] Time to reboot computer ...")
cmd_auto_reboot = 'shutdown -r 05:00'
os.system(cmd_auto_reboot)


'''Check internet available or not'''
print("[INFO] Checking internet ...")
checking_internet()


'''Send infomation to server first'''
with open(os.path.join(os.getcwd(), 'info.json'), "r") as outfile:
    info_json = json.load(outfile)
    IPCAM = info_json['ip_camera']
    IPEDGECOM = info_json['ip_edgecom']
    USERCAM = info_json['user_camera']
    PASSWORDCAM = info_json['password_camera']
    PORTCAM = info_json['port_camera']
    CHANNELCAM = info_json['channel_camera']
    CAMTYPE = info_json['type_camera']


'''Check camera type to get URL'''
if CAMTYPE == 'Dahua' or CAMTYPE == 'HIK':
    URL = f'rtsp://{USERCAM}:{PASSWORDCAM}@{IPCAM}:{PORTCAM}/cam/realmonitor?channel={CHANNELCAM}&subtype=1' # camera Dahua
elif CAMTYPE == 'Ezviz':
    URL = f'rtsp://{USERCAM}:{PASSWORDCAM}@{IPCAM}:{PORTCAM}/onvif{CHANNELCAM}' # camera Ezviz


app = Flask(__name__)
CORS(app)


'''Load frame from camera to get H and W'''
cap = VideoStream(URL).start()
frame = cap.read()
height = frame.shape[0]
width = frame.shape[1]
update_frame_dimension(height, width) # Write H and W to json file


'''Initialize the camera for the first time on the server with information from the json file'''
with open(os.path.join(os.getcwd(), 'info.json'), "r") as outfile:
    info_json = json.load(outfile)
    initialize_information_to_server(info_json)


'''Get information from server and update into json file'''
get_information_from_server(IPCAM, IPEDGECOM, type_cam = True)


time.sleep(5)


@app.route('/')
def index():
    return '[INFO] Running ...'


'''Detect object on input image'''
def detect(ip_camera):
    while True:
        with open(os.path.join(os.getcwd(), 'info.json'), "r") as outfile:
            info_json = json.load(outfile)
            PTS = info_json['coordinate']
            IDENTIFICATIONTIME = info_json['identification_time']        
        frame = cap.read()
        time.sleep(IDENTIFICATIONTIME)
        named_tuple = time.localtime() 
        time_string = time.strftime("%d-%m-%Y %H:%M:%S", named_tuple)
        print(f"[INFO] Detect on {time_string}.")
        detect_method(frame, ip_camera, device, PTS)


'''Send health check camera to server'''
def send_healthcheck(ip_edgecom):
    while True:
        time.sleep(60)
        named_tuple = time.localtime() 
        time_string = time.strftime("%d-%m-%Y %H:%M:%S", named_tuple)
        print(f"[INFO] Sending health check notification on {time_string}.")  
        health_check_nano(ip_edgecom)


''' Read the camera frame'''
def generate():
    frame_rate = 1 # Frame per second
    prev = 0 # Previous frame time    
    while True:
        time_elapsed = time.time() - prev
        frame = cap.read()
        if time_elapsed > 1./frame_rate:
            prev = time.time()        
            (flag, encodedImage) = cv2.imencode(".jpg", frame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
            # yield the output frame in the byte format
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                bytearray(encodedImage) + b'\r\n')
        


'''Read the camera resize frame'''
def generate_resize():
    frame_rate = 1 # Frame per second
    prev = 0 # Previous frame time       
    while True:
        time_elapsed = time.time() - prev
        frame = cap.read()
        if time_elapsed > 1./frame_rate:
            prev = time.time()     
            frame_resize = cv2.resize(frame, (853, 480))
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


@app.route("/api/camera003/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")


@app.route("/api/camera003/video_feed_resize")
def video_feed_resize():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate_resize(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")


@app.route('/api/camera003/download_model', methods=['POST'])
def download():
    try:
        file = request.files['file']
        file.save('./resources/weight_init/best.pt') 
        mess = '[INFO] Model saved!'
        return jsonify(status_code = 200, content={'message':mess})
    except SystemError as error:
        mess = '[INFO] Save model fail ...'
        return jsonify(status_code = 400, content={"success":"false", "error": str(error)})


@app.route('/api/camera003/update_info', methods=['POST'])
def update_info():
    try:
        get_information_from_server(IPCAM, IPEDGECOM, type_cam = False)
        mess = '[INFO] Update information done!'
        return jsonify(status_code = 200, content={'message':mess})
    except SystemError as error:
        mess = '[INFO] Update information fail ...'
        return jsonify(status_code = 400, content={"success":"false", "error": str(error)})


@app.route('/api/camera003/reboot', methods = ['GET'])
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

    time.sleep(10)

    host = settings.HOST
    port = int(settings.PORT)
    app.run(host=host, port=port, debug=False)    
    
# release the video stream pointer
cap.stop()
signal.signal(signal.SIGINT, handler)

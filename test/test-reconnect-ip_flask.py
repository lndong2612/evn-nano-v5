import os
import sys
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))
import cv2
import time
import datetime
import json
from flask import Flask, Response
from utils.function import VideoStream

with open(os.path.join(os.getcwd(), 'info.json'), "r") as outfile:
    info_json = json.load(outfile)
    IPCAM = info_json['ip_camera']
    IPEDGECOM = info_json['ip_edgecom']
    USERCAM = info_json['user_camera']
    PASSWORDCAM = info_json['password_camera']
    PORTCAM = info_json['port_camera']
    RTSP_FORMAT = info_json['rtsp_format']
URL = f'rtsp://{USERCAM}:{PASSWORDCAM}@{IPCAM}:{PORTCAM}/{RTSP_FORMAT}'


app = Flask(__name__)


@app.route('/')
def index():
    return '[INFO] Running ...'


@app.route("/api/video_feed_resize")
def video_feed_resize():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(connect_camera(URL),
        mimetype = "multipart/x-mixed-replace; boundary=frame")


def reset_attempts():
    return 50


def process_video(attempts, camera):
    while(True):
        (grabbed, frame) = camera.read()
        if not grabbed:
            print("[INFO] Disconnected!")
            camera.release()

            if attempts > 0:
                time.sleep(5)
                return True
            else:
                return False
        else:
            '''Read the camera resize frame'''
            frame_resize_output = cv2.resize(frame, (853, 480))
            (flag, encodedImage) = cv2.imencode(".jpg", frame_resize_output)
            # ensure the frame was successfully encoded
            if not flag:
                continue
            # yield the output frame in the byte format
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                bytearray(encodedImage) + b'\r\n')


def connect_camera(URL):
    recall = True
    attempts = reset_attempts()

    while(recall):
        camera = VideoStream(URL).start()

        if camera.open().isOpened():
            print("[INFO] Camera connected at " +
                datetime.datetime.now().strftime("%m-%d-%Y %I:%M:%S%p"))
            attempts = reset_attempts()
            recall = process_video(attempts, camera)
            return recall

        else:
            print("[INFO] Camera not opened " +
                datetime.datetime.now().strftime("%m-%d-%Y %I:%M:%S%p"))
            camera.release()
            attempts -= 1
            print("[INFO] Attempts: " + str(attempts))

            # give the camera some time to recover
            for i in range(5):
                print(f'Time: {i+1}s')
                time.sleep(1)

            continue
       

if __name__ == "__main__":
    # p1 = threading.Thread(target=connect_camera, args=(URL, ))
    # p1.daemon = True
    # p1.start()
    # time.sleep()
    app.run(host='0.0.0.0', port='9298', debug=False)

import os
import sys
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))
import cv2
import time
import datetime
import threading
from flask import Flask, Response
from utils.function import VideoStream


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


'''Camera Ezviz'''
# URL = 'rtsp://admin:CHBAJT@10.10.10.36:554/onvif1'

'''Camera Trong Hau'''
# URL = 'rtsp://admin:Admin12345@tronghau8.kbvision.tv:37779/cam/realmonitor?channel=1&subtype=0'

# USER = 'admin'
# PASSWORD = 'CHBAJT'
# IPADDRESS = '10.10.10.36'
# PORT = '554'
# RTSP_FORMAT = 'onvif1'


'''Camera HIK'''
USER = 'admin'
PASSWORD = 'thinklabs@36'
IPADDRESS = '10.10.10.29'
PORT = '554'
RTSP_FORMAT = 'Streaming/Channels/101'

URL = f"rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/{RTSP_FORMAT}"        

if __name__ == "__main__":
    # p1 = threading.Thread(target=connect_camera, args=(URL, ))
    # p1.daemon = True
    # p1.start()
    # time.sleep()
    app.run(host='0.0.0.0', port='9298', debug=False)

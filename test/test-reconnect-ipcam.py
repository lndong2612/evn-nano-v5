import cv2
import datetime
import time
from imutils.video import VideoStream

def reset_attempts():
    return 50

def process_video(attempts, camera):

    while(True):
        (grabbed, frame) = camera.read()

        if not grabbed:
            print("Disconnected!")
            camera.release()

            if attempts > 0:
                time.sleep(5)
                return True
            else:
                return False
        else:
            cv2.imshow('video output', cv2.resize(frame,(1080, 720)))
            if cv2.waitKey(1) & 0XFF == ord('q'):
                break

def connect_camera(URL):
    recall = True
    attempts = reset_attempts()


    while(recall):
        # camera = cv2.VideoCapture('rtsp://admin:CHBAJT@10.10.10.36:554/live0.264')
        # camera = VideoStream(URL).start()
        camera = cv2.VideoCapture(URL)

        if camera.isOpened():
            print("[INFO] Camera connected at " +
                datetime.datetime.now().strftime("%m-%d-%Y %I:%M:%S%p"))
            attempts = reset_attempts()
            recall = process_video(attempts, camera)
        else:
            print("[INFO] Camera not opened " +
                datetime.datetime.now().strftime("%m-%d-%Y %I:%M:%S%p"))
            camera.release()
            attempts -= 1
            print("Attempts: " + str(attempts))

            # give the camera some time to recover
            time.sleep(5)
            continue

# URL = 'rtsp://admin:CHBAJT@10.10.10.36:554/onvif1' # camera Ezviz
USER = 'admin'
PASSWORD = 'thinklabs@36'
IPADDRESS = '10.10.10.29'
PORT = '554'
URL = f"rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/cam/realmonitor?channel=1&subtype=1"        
# URL = 'rtsp://admin:Admin12345@tronghau8.kbvision.tv:37779/cam/realmonitor?channel=1&subtype=0'
connect_camera(URL)
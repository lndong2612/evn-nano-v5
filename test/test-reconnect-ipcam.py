import os
import sys
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))
import cv2
import time
import datetime
from utils.function import VideoStream

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
            cv2.imshow('* LIVE *', cv2.resize(frame, (1080, 720)))
            if cv2.waitKey(1) & 0XFF == ord('q'):
                break

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
    
    connect_camera(URL)

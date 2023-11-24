import cv2
import datetime
import time

def reset_attempts():
    return 50

def process_video(attempts):

    while(True):
        (grabbed, frame) = camera.read()

        if not grabbed:
            print("disconnected!")
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

recall = True
attempts = reset_attempts()
URL = 'rtsp://admin:CHBAJT@10.10.10.36:554/onvif1' # camera Ezviz
while(recall):
    camera = cv2.VideoCapture('rtsp://admin:CHBAJT@10.10.10.36:554/live0.264')

    if camera.isOpened():
        print("[INFO] Camera connected at " +
              datetime.datetime.now().strftime("%m-%d-%Y %I:%M:%S%p"))
        attempts = reset_attempts()
        recall = process_video(attempts)
    else:
        print("[INFO] Camera not opened " +
              datetime.datetime.now().strftime("%m-%d-%Y %I:%M:%S%p"))
        camera.release()
        attempts -= 1
        print("Attempts: " + str(attempts))

        # give the camera some time to recover
        time.sleep(5)
        continue
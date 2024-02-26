import cv2
import time
from threading import Thread
from utils.function import VideoStream

'''Load frame from camera to get H and W'''
USER = 'admin'
PASSWORD = 'thinklabs@36'
IPADDRESS = '10.10.10.29'
PORT = '554'
URL = f"rtsp://{USER}:{PASSWORD}@{IPADDRESS}:{PORT}/cam/realmonitor?channel=1&subtype=1"

# class WebcamVideoStream:
#     def __init__(self, src=0, name="WebcamVideoStream"):
# 		# initialize the video camera stream and read the first frame
#         self.src = src
# 		# from the stream
#         self.stream = cv2.VideoCapture(self.src)
#         (self.grabbed, self.frame) = self.stream.read()

# 		# initialize the thread name
#         self.name = name

# 		# initialize the variable used to indicate if the thread should
# 		# be stopped
#         self.stopped = False

#     def start(self):
# 		# start the thread to read frames from the video stream
#         t = Thread(target=self.update, name=self.name, args=())
#         t.daemon = True
#         t.start()
#         return self

#     def update(self):
#         while(self.stream.isOpened()):
#             # keep looping infinitely until the thread is stopped
#             while True:
#                 # if the thread indicator variable is set, stop the thread
#                 if self.stopped:
#                     return

#                 # otherwise, read the next frame from the stream
#                 (self.grabbed, self.frame) = self.stream.read()
#         else:
#             self.stream = cv2.VideoCapture(self.src)
#             while True:
#                 # if the thread indicator variable is set, stop the thread
#                 if self.stopped:
#                     return

#                 # otherwise, read the next frame from the stream
#                 (self.grabbed, self.frame) = self.stream.read()
                
#     def read(self):
# 		# return the frame most recently read
#         return self.grabbed, self.frame

#     def stop(self):
# 		# indicate that the thread should be stopped
#         self.stopped = True
    
# class VideoStream:
#     def __init__(self, src=0):
# 		# using OpenCV so initialize the webcam stream
#         self.stream = WebcamVideoStream(src=src)

#     def start(self):
# 		# start the threaded video stream
#         return self.stream.start()

#     def update(self):
# 		# grab the next frame from the stream
#         self.stream.update()

#     def read(self):
# 		# return the current frame
#         return self.stream.read()

#     def stop(self):
# 		# stop the thread and release any resources
#         self.stream.stop()

'''Load frame from camera to get H and W'''
cap = VideoStream(URL).start()
while True:
    grabbed, frame = cap.read()
    if grabbed is True:
        cv2.imshow('LIVE', cv2.resize(frame,(1080, 720)))
        if cv2.waitKey(1) & 0XFF == ord('q'):
            break
    else:
        print("[INFO] Camera disconnected ...")
        time.sleep(5)
        continue

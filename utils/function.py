import os
import sys 
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))
import re
import cv2
import json
import time
import math
import requests
import traceback
import numpy as np
from pathlib import Path
from config import settings
from threading import Thread
from shapely.geometry import Polygon
from imutils.video import VideoStream
from detect import get_detected_object
from urllib.request import urlopen as url
from utils.plots import draw_object_bboxes, draw_detect_bboxes, convert_name_id

# send notifications when unusual object was detected
def post_notification(data_send, ip_camera, messages):
    try:
        result = ', '.join(messages)
        url = f"{settings.URLSV}/warning"
        payload={'content': result,
        'object': data_send['objects'],
        'camera_ip': ip_camera,
        'confirm_status': 'CHUA_XAC_NHAN'}
        files=[
            ('file',(data_send['img_name'],open(data_send['detected_image_path'],'rb'),'image/jpeg'))
        ]
        headers = {}

        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        print(response.text)
    except:
        print("[INFO] Send notifications failed")
        print('[INFO] Error:')
        traceback.print_exc() 
        pass

# send status of edge com
def health_check_nano(ip_edgecom):
    try:
        url = f"{settings.URLSV}/jetson/status/{ip_edgecom}"
        payload="{\r\n    \"status\": true\r\n}"
        headers = {
        'Content-Type': 'application/json'
        }
        response = requests.request("PUT", url, headers=headers, data=payload)
        print(response.text)
    except:
        print("[INFO] Send health check failed")
        print('[INFO] Error:')
        traceback.print_exc() 
        pass

def detect_method(image, ip_camera, device, pts):
    try:
        """Detect object on input image"""
        weight_path = os.path.join(settings.MODEL, 'best.pt') # model path

        input_image = f'{settings.IMAGE_FOLDER}/original.jpg' # original image path
        cv2.imwrite(input_image, image) # save original image

        classified = get_detected_object(weight_path, device, settings.DATA_COCO, input_image) # objects detection on image

        if len(classified) != 0:
            classified_overlap = check_overlap(classified, pts)  
            if len(classified_overlap) != 0:
                im_draw_detect_box = draw_detect_bboxes(image, pts) # drawing detect bboxes
                im_show = draw_object_bboxes(im_draw_detect_box, classified_overlap) # drawing object bboxes
                cv2.imwrite(f'{settings.IMAGE_FOLDER}/detected.jpg', im_show)

                # # save image to use for train
                # time_tuple = time.localtime()
                # time_string = time.strftime('%Y%m%d_%H%M%S', time_tuple)
                # data_image = f'{settings.DATA_IMAGE_FOLDER}/{time_string}.jpg'
                # cv2.imwrite(data_image, im_show)
                
                # get infomation
                status, messages = get_message(classified)
                try:
                    post_notification(status, ip_camera, messages) # send notification to server
                    print('[INFO] Detected!!')
                except UnboundLocalError:
                    pass
     
        else:
            print('[INFO] Good!')
    except:
        print("[INFO] Detect object failed.")
        print('[INFO] Error:')
        traceback.print_exc() 


# Update information from server into json file
def get_information_from_server(ip_camera, ip_edcom, type_cam):
    try:
        url = f"https://tcamera.thinklabs.com.vn/api/camera/getCameraByIp/{ip_camera}"

        payload="{\r\n    \"jetson_ip_address\":\"" + f"{ip_edcom}" "\"\r\n}"
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        info = response.text
        res = json.loads(info)
        for information in res['data']:
            coor = information['detect_point']
            time_detect = information['identification_time']
            brand_name = information['type_id']['brand']

        json_file = open(os.path.join(os.getcwd(), 'info.json'), "r")
        data = json.load(json_file)
        json_file.close()
        data['identification_time'] = time_detect

        if type_cam == True:
            data['type_camera'] = brand_name
        else:
            pass

        data['coordinate'] = coor

        # Save our changes to JSON file
        json_file = open(os.path.join(os.getcwd(), 'info.json'), "w+")
        json_file.write(json.dumps(data, indent = 5))
        json_file.close()
        print('[INFO] Update information from server done.')

    except:
        print("[INFO] Update information from server failed.")
        print('[INFO] Error:')
        traceback.print_exc() 


# Write H and W to json file
def update_frame_dimension(height, width):
    try:
        json_file = open(os.path.join(os.getcwd(), 'info.json'), "r")
        data = json.load(json_file)
        json_file.close()
        data['cam_height'] = height
        data['cam_width'] = width

        # Save our changes to JSON file
        json_file = open(os.path.join(os.getcwd(), 'info.json'), "w+")
        json_file.write(json.dumps(data, indent = 5))
        json_file.close()
        print("[INFO] Update frame dimension done.")

    except:
        print("[INFO] Update frame dimension failed.")
        print('[INFO] Error:')
        traceback.print_exc()      

# Create new camera for the first time
def initialize_information_to_server(info):
    try:
        NAMECAM = info['name_camera']
        IPCAM = info['ip_camera']  
        USERCAM = info['user_camera']
        PASSWORDCAM = info['password_camera']
        PORTCAM = info['port_camera']
        IDENTIFICATIONTIME = info['identification_time']
        HEIGHTCAM = info['cam_height']
        WIDTHCAM = info['cam_width']

        url = "https://tcamera.thinklabs.com.vn/api/camera"
        payload="{\r\n    \"name\": \"" + f"{NAMECAM}" + "\",\r\n    \"ip_address\": \"" + f"{IPCAM}" + "\",\r\n    \"username\": \"" + f"{USERCAM}" + "\",\r\n    \"password\": \"" + f"{PASSWORDCAM}" + "\",\r\n    \"port\": \"" + f"{PORTCAM}" + "\",\r\n    \"cam_width\": \"" + f"{WIDTHCAM}" + "\",\r\n    \"cam_height\": \"" + f"{HEIGHTCAM}" + "\",\r\n    \"identification_time\": \"" + f"{IDENTIFICATIONTIME}" + "\",\r\n    \"status\": true\r\n}"
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print('[INFO] Create information on server done.')
    except:
        print("[INFO] Create information on server failed.")
        print('[INFO] Error:')
        traceback.print_exc()

# Ping to check internet
def checking_internet():
    status = ''
    while(True):
        try:
            url('https://google.com.vn/', timeout=3)
            status = True
        except Exception as e:
            status = False
        
        if status == True:
            print('[INFO] Internet is available.')
            break
        else:
            print('[INFO] Internet is not available.')
            time.sleep(5)
            continue

# Ping to check camera
def checking_camera(URL):
    while(True):
        cap = VideoStream(URL).start()
        grabbed, frame = cap.read()
        if not grabbed:
            print('[INFO] Connect camera done!!')
            break
        else:
            print('[INFO] Fail, connect camera again ...')
            time.sleep(5)
            continue    
    
    return frame, grabbed

class WebcamVideoStream:
    def __init__(self, src=0, name="WebcamVideoStream"):
		# initialize the video camera stream and read the first frame
        self.src = src
		# from the stream
        self.stream = cv2.VideoCapture(self.src)
        (self.grabbed, self.frame) = self.stream.read()

		# initialize the thread name
        self.name = name

		# initialize the variable used to indicate if the thread should
		# be stopped
        self.stopped = False

    def start(self):
		# start the thread to read frames from the video stream
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
		# return the frame most recently read
        return self.grabbed, self.frame

    def stop(self):
		# indicate that the thread should be stopped
        self.stopped = True

class VideoStream:
    def __init__(self, src=0):
		# using OpenCV so initialize the webcam stream
        self.stream = WebcamVideoStream(src=src)

    def start(self):
		# start the threaded video stream
        return self.stream.start()

    def update(self):
		# grab the next frame from the stream
        self.stream.update()

    def read(self):
		# return the current frame
        return self.stream.read()

    def stop(self):
		# stop the thread and release any resources
        self.stream.stop()


def clean_str(s):
    # Cleans a string by replacing special characters with underscore _
    return re.sub(pattern='[|@#!¡·$€%&()=?¿^*;:,¨´><+]', repl='_', string=s)


def letterbox(im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
    # Resize and pad image while meeting stride-multiple constraints
    shape = im.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better val mAP)
        r = min(r, 1.0)

    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return im, ratio, (dw, dh)


class LoadStreams:
    # YOLOv5 streamloader, i.e. `python detect.py --source 'rtsp://example.com/media.mp4'  # RTSP, RTMP, HTTP streams`
    def __init__(self, sources='file.streams', img_size=640, stride=32, auto=True, transforms=None, vid_stride=1):
        self.mode = 'stream'
        self.img_size = img_size
        self.stride = stride
        self.vid_stride = vid_stride  # video frame-rate stride
        sources = Path(sources).read_text().rsplit() if os.path.isfile(sources) else [sources]
        n = len(sources)
        self.sources = [clean_str(x) for x in sources]  # clean source names for later
        self.imgs, self.fps, self.frames, self.threads = [None] * n, [0] * n, [0] * n, [None] * n
        for i, s in enumerate(sources):  # index, source
            # Start thread to read frames from video stream
            st = f'{i + 1}/{n}: {s}... '

            s = eval(s) if s.isnumeric() else s  # i.e. s = '0' local webcam

            cap = cv2.VideoCapture(s)
            assert cap.isOpened(), f'{st}Failed to open {s}'
            # w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            # h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)  # warning: may return 0 or nan
            self.frames[i] = max(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 0) or float('inf')  # infinite stream fallback
            self.fps[i] = max((fps if math.isfinite(fps) else 0) % 100, 0) or 30  # 30 FPS fallback

            _, self.imgs[i] = cap.read()  # guarantee first frame
            self.threads[i] = Thread(target=self.update, args=([i, cap, s]), daemon=True)
            # LOGGER.info(f'{st} Success ({self.frames[i]} frames {w}x{h} at {self.fps[i]:.2f} FPS)')
            self.threads[i].start()
        # LOGGER.info('')  # newline

        # check for common shapes
        s = np.stack([letterbox(x, img_size, stride=stride, auto=auto)[0].shape for x in self.imgs])
        self.rect = np.unique(s, axis=0).shape[0] == 1  # rect inference if all shapes equal
        self.auto = auto and self.rect
        self.transforms = transforms  # optional
        # if not self.rect:
        #     LOGGER.warning('WARNING ⚠️ Stream shapes differ. For optimal performance supply similarly-shaped streams.')

    def update(self, i, cap, stream):
        # Read stream `i` frames in daemon thread
        n, f = 0, self.frames[i]  # frame number, frame array
        while cap.isOpened() and n < f:
            n += 1
            cap.grab()  # .read() = .grab() followed by .retrieve()
            if n % self.vid_stride == 0:
                success, im = cap.retrieve()
                if success:
                    self.imgs[i] = im
                else:
                    # LOGGER.warning('WARNING ⚠️ Video stream unresponsive, please check your IP camera connection.')
                    self.imgs[i] = np.zeros_like(self.imgs[i])
                    cap.open(stream)  # re-open stream if signal was lost
            time.sleep(0.0)  # wait time

    def __iter__(self):
        self.count = -1
        return self

    def __next__(self):
        self.count += 1
        if not all(x.is_alive() for x in self.threads) or cv2.waitKey(1) == ord('q'):  # q to quit
            cv2.destroyAllWindows()
            raise StopIteration

        im0 = self.imgs.copy()
        if self.transforms:
            im = np.stack([self.transforms(x) for x in im0])  # transforms
        else:
            im = np.stack([letterbox(x, self.img_size, stride=self.stride, auto=self.auto)[0] for x in im0])  # resize
            im = im[..., ::-1].transpose((0, 3, 1, 2))  # BGR to RGB, BHWC to BCHW
            im = np.ascontiguousarray(im)  # contiguous

        return self.sources, im, im0, None, ''

    def __len__(self):
        return len(self.sources)  # 1E12 frames = 32 streams at 30 FPS for 30 years

def check_overlap(classified, PTS_Area):
    new_classified = []
    if len(PTS_Area) != 0:
        if len(PTS_Area) == 2:
            xmin = PTS_Area[0][0]
            xmax = PTS_Area[1][0]
            ymin = PTS_Area[0][1]
            ymax = PTS_Area[1][1]
            PTS_Area = [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]]

        for info in classified:
            xmin = info['xmin']
            ymin = info['ymin']
            xmax = info['xmax']
            ymax = info['ymax']
            PTS_Object = [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]]
            polygon1 = Polygon(PTS_Area)
            polygon2 = Polygon(PTS_Object)
            intersect = polygon1.intersection(polygon2).area
            union = polygon1.union(polygon2).area
            iou = intersect / union
            if iou != 0:
                new_classified.append(info)
    else:
        new_classified = classified

    return new_classified

def get_message(classified):
    messages = []
    result = []
    # get infomation
    # initialize an empty dictionary to store label counts
    label_counts = {}

    # iterate over each dictionary in the list
    for item in classified:
        label = item['label']
        label_counts[label] = label_counts.get(label, 0) + 1 # increment the count for the label

    for label, count in label_counts.items():
        vn_label = convert_name_id(label, 'vietnamese_name')
        s = f"Phát hiện {count} {vn_label}"
        messages.append(s)                   
        info_label = {
                "label": label.upper(),
                "numbers": count
            }
        result.append(info_label)

    status = {
        'total_objects' : len(classified),
        'objects': str(result),
        'img_name' : 'detected.jpg',
        'detected_image_path': f'{settings.IMAGE_FOLDER}/detected.jpg'
    }

    return status, messages
import os
import sys 
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))
import cv2
import json
import time
import requests
import traceback
from config import settings
from threading import Thread
from detect import get_detected_object
from shapely.geometry import Polygon
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


def detect_method(image, ip_camera, pts, conf_thres, iou_thres, model, pt, bs, imgsz, names, stride):
    try:
        input_image = f'{settings.IMAGE_FOLDER}/original.jpg' # original image path
        cv2.imwrite(input_image, image) # save original image

        classified = get_detected_object(input_image, conf_thres, iou_thres, model, pt, bs, imgsz, names, stride, allow_classes=0) # objects detection on image

        if len(classified) != 0:
            classified_overlap = check_overlap(classified, pts)  
            if len(classified_overlap) != 0:
                im_draw_detect_box = draw_detect_bboxes(image, pts) # drawing detect bboxes
                im_show = draw_object_bboxes(im_draw_detect_box, classified_overlap) # drawing object bboxes
                cv2.imwrite(f'{settings.IMAGE_FOLDER}/detected.jpg', im_show)
                
                # get infomation
                status, messages = get_message(classified_overlap)
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


def detect_method2(image, ip_camera, pts, conf_thres, iou_thres, model, pt, bs, imgsz, names, stride, model2, pt2, bs2, imgsz2, names2, stride2):
    try:
        input_image = f'{settings.IMAGE_FOLDER}/original.jpg' # original image path
        cv2.imwrite(input_image, image) # save original image

        classified1 = get_detected_object(input_image, conf_thres, iou_thres, model, pt, bs, imgsz, names, stride, allow_classes=1) # objects detection on image
        classified2 = get_detected_object(input_image, conf_thres, iou_thres, model2, pt2, bs2, imgsz2, names2, stride2, allow_classes=2) # objects detection on image
        classified = classified1 + classified2
        if len(classified) != 0:
            classified_overlap = check_overlap(classified, pts)  
            if len(classified_overlap) != 0:
                im_draw_detect_box = draw_detect_bboxes(image, pts) # drawing detect bboxes
                im_show = draw_object_bboxes(im_draw_detect_box, classified_overlap) # drawing object bboxes
                cv2.imwrite(f'{settings.IMAGE_FOLDER}/detected.jpg', im_show)
                
                # get infomation
                status, messages = get_message(classified_overlap)
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
def get_information_from_server(ip_camera, ip_edcom):
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
            camera_name = information['name']
            time_detect = information['identification_time']
            brand_name = information['type_id']['brand']
            api_name = information['api_name']          
            coor = information['detect_point']

        json_file = open(os.path.join(os.getcwd(), 'info.json'), "r")
        data = json.load(json_file)
        json_file.close()
        data['name_camera'] = camera_name      
        data['identification_time'] = time_detect
        data['api_name'] = api_name
        data['type_camera'] = brand_name
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
        if grabbed:
            print('[INFO] Connect camera done!!')
            cap.stop()
            break
        else:
            print('[INFO] Fail, connect camera again ...')
            time.sleep(5)
            continue

    return grabbed, frame

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

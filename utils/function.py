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
from datetime import datetime
from shapely.geometry import Polygon
from detect import get_detected_object_v5
from urllib.request import urlopen as url
from utils.plots import draw_object_bboxes, draw_warning_area, convert_name_id

class WebcamVideoStream:
    def __init__(self, src=0, name="WebcamVideoStream"):
		# initialize the video camera stream and read the first frame
        self.src = src
		# from the stream
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()

		# initialize the thread name
        self.name = name

		# initialize the variable used to indicate if the thread should
		# be stopped
        self.stopped = False

    def open(self):
        return self.stream
    
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

    def release(self):
		# return the frame most recently read
        self.stream.release()

class VideoStream:
    def __init__(self, src=0):
		# otherwise, we are using OpenCV so initialize the webcam
		# stream
        self.stream = WebcamVideoStream(src=src)

    def start(self):
		# start the threaded video stream
        return self.stream.start()
    
    def open(self):
        return self.stream.open()

    def update(self):
		# grab the next frame from the stream
        self.stream.update()

    def read(self):
		# return the current frame
        return self.stream.read()

    def stop(self):
		# stop the thread and release any resources
        self.stream.stop()

    def release(self):
        self.stream.release()


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
                datetime.now().strftime("%m-%d-%Y %I:%M:%S%p"))
            attempts = reset_attempts()
            recall = process_video(attempts, camera)
            return recall

        else:
            print("[INFO] Camera not opened " +
                datetime.now().strftime("%m-%d-%Y %I:%M:%S%p"))
            camera.release()
            attempts -= 1
            print("[INFO] Attempts: " + str(attempts))

            # give the camera some time to recover
            for i in range(5):
                print(f'Time: {i+1}s')
                time.sleep(1)

            continue


'''Send notifications when unusual object was detected'''
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
        print("[INFO] Notifications sent successfully !")
    except:
        print("[INFO] Notifications sent fail !")
        print('[INFO] Error:')
        traceback.print_exc() 
        pass


'''Send health status of edge com to server'''
def health_check_nano(ip_edgecom):
    try:
        url = f"{settings.URLSV}/jetson/status/{ip_edgecom}"
        payload="{\r\n    \"status\": true\r\n}"
        headers = {
        'Content-Type': 'application/json'
        }
        response = requests.request("PUT", url, headers=headers, data=payload)
        print("[INFO] Health check sent successfully !")
    except:
        print("[INFO] Health check sent fail !")
        print('[INFO] Error:')
        traceback.print_exc() 
        pass


def detect_v5_1(image, ip_camera, pts, conf_thres, iou_thres, model, pt, bs, imgsz, names, stride, json_object):
    try:
        input_image = f'{settings.IMAGE_FOLDER}/original.jpg' # original image path
        cv2.imwrite(input_image, image) # save original imag
        classified = get_detected_object_v5(input_image, conf_thres, iou_thres, model, pt, bs, imgsz, names, stride, json_object, allow_classes=0) # objects detection on image with yolov5s        
        if len(classified) != 0:
            classified_overlap = check_overlap(classified, pts)  
            if len(classified_overlap) != 0:
                im_draw_warning_area = draw_warning_area(image, pts) # image drawing warning area
                im_show = draw_object_bboxes(im_draw_warning_area, classified_overlap, json_object) # image drawing object bboxes
                cv2.imwrite(f'{settings.IMAGE_FOLDER}/detected.jpg', im_show)
                
                # get infomation
                print('[INFO] Detected !')
                status, messages = get_message(classified_overlap, json_object)
                print(f'[INFO] {messages}')
                try:
                    post_notification(status, ip_camera, messages) # send notification to server
                except UnboundLocalError:
                    pass
     
        else:
            print('[INFO] Good !')
    except:
        print("[INFO] Detected object fail .")
        print('[INFO] Error:')
        traceback.print_exc() 


def detect_v5_2(image, ip_camera, pts, conf_thres, iou_thres, model, pt, bs, imgsz, names, stride, model2, pt2, bs2, imgsz2, names2, stride2, json_object):
    try:
        input_image = f'{settings.IMAGE_FOLDER}/original.jpg' # original image path
        cv2.imwrite(input_image, image) # save original image

        classified1 = get_detected_object_v5(input_image, conf_thres, iou_thres, model, pt, bs, imgsz, names, stride, json_object, allow_classes=2) # objects detection with model 1
        classified2 = get_detected_object_v5(input_image, conf_thres, iou_thres, model2, pt2, bs2, imgsz2, names2, stride2, json_object, allow_classes=1) # objects detection with model 2
        classified = classified1 + classified2 # combine 2 results
        if len(classified) != 0:
            classified_overlap = check_overlap(classified, pts)  
            if len(classified_overlap) != 0:
                im_draw_warning_area = draw_warning_area(image, pts) # image drawing warning area
                im_show = draw_object_bboxes(im_draw_warning_area, classified_overlap, json_object) # image drawing object bboxes
                cv2.imwrite(f'{settings.IMAGE_FOLDER}/detected.jpg', im_show)
                
                # get infomation
                print('[INFO] Detected !')
                status, messages = get_message(classified_overlap, json_object)
                print(f'[INFO] {messages}')
                try:
                    post_notification(status, ip_camera, messages) # send notification to server
                except UnboundLocalError:
                    pass
     
        else:
            print('[INFO] Good !')
    except:
        print("[INFO] Detected object fail .")
        print('[INFO] Error:')
        traceback.print_exc()


'''Update information from server into json file'''
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
        print('[INFO] Updated information from server successfully .')

    except:
        print("[INFO] Updated information from server fail .")
        print('[INFO] Error:')
        traceback.print_exc()   


'''Write H and W to json file'''
def update_frame_dimension(HEIGHTCAM, WIDTHCAM, IPCAM):
    try:
        url = f"https://tcamera.thinklabs.com.vn/api/camera/updateSizeCamera/{IPCAM}"

        payload = json.dumps({
        "cam_width": WIDTHCAM,
        "cam_height": HEIGHTCAM
        })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("PUT", url, headers=headers, data=payload)        
        print('[INFO] Updated H and W to server successfully .')
    except:
        print("[INFO] Updated H and W to server fail .")
        print('[INFO] Error:')
        traceback.print_exc()


'''Ping to check internet'''
def checking_internet():
    status = ''
    count_seconds = 0
    while(True):
        try:
            url('https://google.com.vn/', timeout=3) # UBUNTU
            # os.system('ping 1.1.1.1') # WIN
            status = True
        except Exception as e:
            status = False
        
        if status == True:
            print('[INFO] Internet is available .')
            break
        else:
            print('[INFO] Internet is not available .')
            print(f'[INFO] Time left to reboot if there is no internet connection: {180 - count_seconds}s.')
            for i in range(5):
                print(f'Time: {i+1}s')
                time.sleep(1)
                count_seconds += 1

            if count_seconds == 180:
                os.system("sudo reboot")
            
            continue


'''Ping to check camera'''
def checking_camera(URL):
    while(True):
        cap = VideoStream(URL).start()
        grabbed, frame = cap.read()
        if grabbed:
            print('[INFO] Connected camera successfully .')
            cap.stop()
            break
        else:
            print('[INFO] Connected camera fail, again ...')
            for i in range(5):
                print(f'Time: {i+1}s')
                time.sleep(1)
            continue

    cap.stop()

    return grabbed, frame



'''Check if bbox of object touch to warning area'''
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


'''Convert to the correct message format to send to the server'''
def get_message(classified, json_object):
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
        vn_label = convert_name_id(label, 'vietnamese_name', json_object)
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

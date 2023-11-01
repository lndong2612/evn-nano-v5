import os
import sys 
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))
import cv2
import requests
from config import settings
from detect import get_detected_object
from utils.plots import draw_bboxes
from config import settings

# send notifications when unusual object was detected
def post_notification(data_send, info_system, messages):
    try:
        result = ', '.join(messages)
        url = f"{settings.URLSV}/warning"
        payload={'content': result,
        'object': data_send['objects'],
        'camera_ip': info_system['ip_camera'],
        'confirm_status': 'CHUA_XAC_NHAN'}
        files=[
            ('file',(data_send['img_name'],open(data_send['detected_image_path'],'rb'),'image/jpeg'))
        ]
        headers = {}

        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        print(response.text)
    except:
        print("[INFO] Send notifications failed")
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
        pass

def detect_method(image, info_system, device):
    try:
        """Detect object on input image"""
        weight_path = os.path.join(settings.MODEL, 'best.pt') # model path

        input_image = '{}/original.jpg'.format(settings.IMAGE_FOLDER) # original image path
        cv2.imwrite(input_image, image)# save original image

        classified, det, result, messages = get_detected_object(weight_path, device, settings.DATA_COCO, input_image) # objects detection on image

        if len(det) != 0:
            im_show = draw_bboxes(image, classified, det) # drawing bboxes on image
            output_image = '{}/detected.jpg'.format(settings.IMAGE_FOLDER)
            cv2.imwrite(output_image, im_show)
            
            # get infomation
            status = {
                'total_objects' : len(det),
                'objects': str(result),
                'img_name' : 'detected.jpg',
                'detected_image_path': output_image,
            }
            print(status)
            try:
                post_notification(status, info_system, messages)# send notification to server
            except UnboundLocalError:
                pass
     
        else:
            print('[INFO] Good!')

    except Exception as error:
        print("[INFO] Detect object failed")
        print('Error: ', error)
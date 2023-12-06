import os
import sys 
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))
import cv2
import json
import time
import requests
from config import settings
from utils.general import LOGGER
from detect import get_detected_object
from utils.plots import draw_object_bboxes, draw_detect_bboxes

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
        LOGGER.info(response.text)
    except Exception as error:
        LOGGER.info("[INFO] Send notifications failed")
        LOGGER.info('[INFO] Error: ', error)
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
        LOGGER.info(response.text)
    except Exception as error:
        LOGGER.info("[INFO] Send health check failed")
        LOGGER.info('[INFO] Error: ', error)
        pass

def detect_method(image, info_system, device, pts):
    try:
        """Detect object on input image"""
        weight_path = os.path.join(settings.MODEL, 'best.pt') # model path

        input_image = '{}/original.jpg'.format(settings.IMAGE_FOLDER) # original image path
        cv2.imwrite(input_image, image) # save original image

        classified, det, result, messages = get_detected_object(weight_path, device, settings.DATA_COCO, input_image, pts) # objects detection on image

        if len(det) != 0:
            im_draw_detect_box = draw_detect_bboxes(image, pts) # drawing detect bboxes
            im_show = draw_object_bboxes(im_draw_detect_box, classified) # drawing object bboxes
            output_image = '{}/detected.jpg'.format(settings.IMAGE_FOLDER)
            cv2.imwrite(output_image, im_show)

            # save image to use for train
            time_tuple = time.localtime()
            time_string = time.strftime('%Y%m%d_%H%M%S', time_tuple)
            data_image = '{}/{}.jpg'.format(settings.DATA_IMAGE_FOLDER, time_string)
            cv2.imwrite(data_image, im_show)      
            
            # get infomation
            status = {
                'total_objects' : len(det),
                'objects': str(result),
                'img_name' : 'detected.jpg',
                'detected_image_path': output_image,
            }
            try:
                post_notification(status, info_system, messages) # send notification to server
            except UnboundLocalError:
                pass
     
        else:
            LOGGER.info('[INFO] Good!')
    except Exception as error:
        LOGGER.info("[INFO] Detect object failed.")
        LOGGER.info('[INFO] Error: ', error)


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
        LOGGER.info('[INFO] Update information from server done.')

    except Exception as error:
        LOGGER.info("[INFO] Update information from server failed.")
        LOGGER.info('[INFO] Error: ', error)


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
        LOGGER.info("[INFO] Update frame dimension done.")

    except Exception as error:
        LOGGER.info("[INFO] Update frame dimension failed.")
        LOGGER.info('[INFO] Error: ', error)        

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
        LOGGER.info('[INFO] Create information on server done.')
    except Exception as error:
        LOGGER.info("[INFO] Create information on server failed.")
        LOGGER.info('[INFO] Error: ', error)     
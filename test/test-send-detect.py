# import os
# import sys
# WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.join(WORKING_DIR, "../"))
# import json
# import requests
# from config import settings

# # send notifications when unusual object was detected
# def post_notification(data_send, info_system, messages):
#     try:
#         result = ', '.join(messages)
#         url = f"{settings.URLSV}/warning"
#         payload={'content': result,
#         'object': data_send['objects'],
#         'camera_ip': info_system['ip_camera'],
#         'confirm_status': 'CHUA_XAC_NHAN'}
#         files=[
#             ('file',(data_send['img_name'],open(data_send['detected_image_path'],'rb'),'image/jpeg'))
#         ]
#         headers = {}

#         response = requests.request("POST", url, headers=headers, data=payload, files=files)
#         print(response.text)
#     except Exception as error:
#         print("[INFO] Send notifications failed")
#         print('[INFO] Error: ', error)
#         pass


# # get infomation
# status = {
#     'total_objects' : 1,
#     'objects': 'Cay',
#     'img_name' : 'warning.jpg',
#     'detected_image_path': './test/images/objects/warning.jpg',
# }

# '''Send infomation to server first'''
# with open(os.path.join(os.getcwd(), 'info.json'), "r") as outfile:
#     messages = 'Canh bao'
#     info_json = json.load(outfile)
#     post_notification(status, info_json, messages)
import time
from datetime import datetime

t1 = datetime.now()

time.sleep(5)

print(datetime.now() - t1)
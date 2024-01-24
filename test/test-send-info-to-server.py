import os
import sys
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))
import json
import requests

def update_infomation_to_server(info):
    print(info)
    NAMECAM = info['name_camera']
    IPCAM = info_json['ip_camera']  
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

    print(response.text)


'''Send infomation to server first'''
with open(os.path.join(os.getcwd(), 'info.json'), "r") as outfile:
    info_json = json.load(outfile)
    update_infomation_to_server(info_json)
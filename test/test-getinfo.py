import os
import sys
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))
import requests
import json
# ip_camera = "10.10.10.36" 
# ip_edcom = "10.10.10.63"   

ip_camera = "10.10.10.100" 
ip_edcom = "10.10.10.90"    
url = f"https://tcamera.thinklabs.com.vn/api/camera/getCameraByIp/{ip_camera}"

payload="{\r\n    \"jetson_ip_address\":\"" + f"{ip_edcom}" "\"\r\n}"
headers = {
'Content-Type': 'application/json'
}

response = requests.request("GET", url, headers=headers, data=payload)

info = response.text
res = json.loads(info)

for infomation in res['data']:
    coor = infomation['detect_point']
    time_detect = infomation['identification_time']
    brand_name = infomation['type_id']['brand']

jsonFile = open(os.path.join(os.getcwd(), 'info.json'), "r")
data = json.load(jsonFile)
jsonFile.close()
data['identification_time'] = time_detect
data['type_camera'] = brand_name
data['coordinate'] = coor

# Save our changes to JSON file
jsonFile = open(os.path.join(os.getcwd(), 'info.json'), "w+")
jsonFile.write(json.dumps(data, indent = 5))
jsonFile.close()

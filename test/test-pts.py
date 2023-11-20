import os
import requests
import json

ip_camera = "10.10.10.100"
ip_edcom = "10.10.10.90"
url = f"https://tcameradev.thinklabs.com.vn/api/camera/getCameraByIp/{ip_camera}"

payload="{\r\n    \"jetson_ip_address\":\"" + f"{ip_edcom}" "\"\r\n}"
headers = {
'Content-Type': 'application/json'
}

response = requests.request("GET", url, headers=headers, data=payload)

info = response.text
res = json.loads(info)
coor_arr = []
for infomation in res['data']:
    coor = infomation['detect_point']
    coor_arr.append(coor)

entry = {'coordinate': coor_arr}
# info_update = {'coordinate':coor_arr}
with open(os.path.join(os.getcwd(), 'info.json'), "r+") as file:
    file_data = json.load(file)
    file_data.update(entry)
    file.seek(0)
    json.dump(file_data, file, indent = 4)

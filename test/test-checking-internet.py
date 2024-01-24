import os
from urllib.request import urlopen as url
import requests
import socket 
import time
def checking_internet():
    hostname = "8.8.8.8"

    while(True):
        packetloss = os.system("ping " + hostname)
        if packetloss == 0:
            print('[INFO] Connect internet successful!')
            break
        else:
            print('[INFO] Connect internet unsuccessful. Continue ...')
            continue
       
def checking_internet_ubuntu():
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

checking_internet_ubuntu()

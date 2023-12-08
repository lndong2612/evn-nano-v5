import os

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
       

checking_internet()

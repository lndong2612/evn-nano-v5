import os
import sys
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))
import cv2
import json
import time
from config import settings
from detect import get_detected_object
from utils.plots import draw_object_bboxes, draw_detect_bboxes
from utils.function import post_notification, check_overlap, get_message
import traceback 

## pts of rectangle
# pts =[[128,250],[430,520]]
# pts = [[70,48],[525,273]]

## pts of polygon
# pts = [[102, 331], [307, 344], [279, 538], [49, 546]]

## pts of null
pts = []

device = '' # cuda device, i.e. 0 or 0,1,2,3 or cpu

"""Detect object on input image"""
weight_path = 'resources/weight_init/best.pt' # model path

input_image = 'test/images/objects/evn3.jpg' # original image path
image = cv2.imread(input_image)

# cv2.imwrite(input_image, image) # save original image

classified = get_detected_object(weight_path, device, settings.DATA_COCO, input_image) # objects detection on image
try:
    if len(classified) != 0:
        classified_overlap = check_overlap(classified, pts)      
        if len(classified_overlap) != 0:
            im_draw_detect_box = draw_detect_bboxes(image, pts) # drawing detect bboxes
            im_show = draw_object_bboxes(im_draw_detect_box, classified_overlap) # drawing object bboxes
            output_image = 'detected.jpg'
            cv2.imwrite(output_image, im_show)

            # save image to use for train
            time_tuple = time.localtime()
            time_string = time.strftime('%Y%m%d_%H%M%S', time_tuple)
            data_image = '{}/{}.jpg'.format(settings.DATA_IMAGE_FOLDER, time_string)
            cv2.imwrite(data_image, im_show)      


            status, messages =  get_message(classified)
            print(status)
            print(messages)
            info_system = '10.10.10.36'
            # post_notification(status, info_system, messages) # send notification to server
        else:
            pass
    else:
        print('[INFO] Good!')
except:
    print('[INFO] Error:')
    traceback.print_exc() 
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
from utils.function import detect_method, post_notification
import traceback 

input_image_name = 'original.jpg'
input_image_path = f'./test/images/objects/{input_image_name}'
image = cv2.imread(input_image_path)

## pts of rectangle
# pts =[[128,250],[430,520]]
# pts = [[70,48],[525,273]]

## pts of polygon
# pts = [[102, 331], [307, 344], [279, 538], [49, 546]]

## pts of null
# pts = []


# with open(os.path.join(os.getcwd(), 'info.json'), "r") as outfile:
#     info_json = json.load(outfile)
#     pts = info_json['coordinate']
# print(pts)
# image = cv2.imread(input_image_path)
# device = '' # cuda device, i.e. 0 or 0,1,2,3 or cpu
# weight_path = os.path.join(settings.MODEL, 'best.pt') # model path

# classified, det, result, messages = get_detected_object(weight_path, device, settings.DATA_COCO, input_image_path, pts) # objects detection on image
# im_draw_detect_box = draw_detect_bboxes(image, pts) # drawing detect bboxes
# im_show = draw_object_bboxes(im_draw_detect_box, classified) # drawing object bboxes
# # cv2.imwrite(save_image_path, im_show)
# cv2.imshow('show', im_show)
# cv2.waitKey(0)
device = '' # cuda device, i.e. 0 or 0,1,2,3 or cpu
pts = []

"""Detect object on input image"""
weight_path = os.path.join(settings.MODEL, 'best.pt') # model path

input_image = '{}/original.jpg'.format(settings.IMAGE_FOLDER) # original image path
cv2.imwrite(input_image, image) # save original image

classified, det, result, messages = get_detected_object(weight_path, device, settings.DATA_COCO, input_image, pts) # objects detection on image
try:
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
        # try:
        #     info_system = '10.10.10.36'
        #     post_notification(status, info_system, messages) # send notification to server
        # except UnboundLocalError:
        #     pass
        info_system = '10.10.10.36'
        post_notification(status, info_system, messages) # send notification to server

    else:
        print('[INFO] Good!')
except:
    print('[INFO] Error:')
    traceback.print_exc() 
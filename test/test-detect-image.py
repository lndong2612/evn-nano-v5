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
import time
from detect import load_model
## pts of rectangle
# pts =[[128,250],[430,520]]
# pts = [[70,48],[525,273]]

## pts of polygon
# pts = [[102, 331], [307, 344], [279, 538], [49, 546]]

## pts of null
pts = []

device = '' # cuda device, i.e. 0 or 0,1,2,3 or cpu

"""Detect object on input image"""
weight_path2 = 'resources/weight_init/best2.pt' # model path

"""Detect object on input image"""
weight_path = os.path.join(settings.MODEL, 'best.pt') # model path
model, pt, bs, imgsz, names, stride = load_model(weight_path, device, settings.DATA_COCO)
model2, pt2, bs2, imgsz2, names2, stride2 = load_model(weight_path2, device, settings.DATA_COCO)

input_image = 'datatest/images/fire-tree2.jpg' # original image path
image = cv2.imread(input_image)

# cv2.imwrite(input_image, image) # save original image
conf_thres = 0.2 # confidence threshold
iou_thres = 0.4 # NMS IOU threshold
classified1 = get_detected_object(input_image, conf_thres, iou_thres, model, pt, bs, imgsz, names, stride, allow_classes=1) # objects detection on image
classified2 = get_detected_object(input_image, conf_thres, iou_thres, model2, pt2, bs2, imgsz2, names2, stride2, allow_classes=2) # objects detection on image
time_tuple = time.localtime()
time_string = time.strftime('%d%m%Y%H%M%S')
classified = classified1 + classified2

# print("classified",classified)
# print("\n")
# print("classified1",classified1)
# print("\n")
# print("classified2",classified2)
try:
    if len(classified) != 0:
        classified_overlap = check_overlap(classified, pts)      
        if len(classified_overlap) != 0:
            im_draw_detect_box = draw_detect_bboxes(image, pts) # drawing detect bboxes
            im_show = draw_object_bboxes(im_draw_detect_box, classified_overlap) # drawing object bboxes
            output_image = f'datatest/results/detected_{time_string}.jpg'
            cv2.imwrite(output_image, im_show)

            # save image to use for train
            time_tuple = time.localtime()
            time_string = time.strftime('%Y%m%d_%H%M%S', time_tuple)
            data_image = '{}/{}.jpg'.format(settings.DATA_IMAGE_FOLDER, time_string)
            cv2.imwrite(data_image, im_show)      


            status, messages = get_message(classified_overlap)
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
import os
import sys
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))
import cv2
import json
import time
from config import settings
from detect import get_detected_object
from utils.plots import draw_object_bboxes, draw_warning_area
from utils.function import post_notification, check_overlap, get_message
import traceback 
import time
from detect import load_model
## pts of rectangle
# pts =[[128,250],[430,520]]
# pts = [[70,48],[525,273]]

## pts of polygon
# pts = [[102, 331], [307, 344], [330, 350],[260, 530], [279, 538], [49, 546]]

## pts of null
pts = []

device = '' # cuda device, i.e. 0 or 0,1,2,3 or cpu

"""Detect object on input image"""
weight_path2 = 'resources/weight_init/best.pt' # model path
with open('object.json', 'r',encoding='utf-8') as outfile:
    json_object = json.load(outfile)
"""Detect object on input image"""
weight_path = os.path.join(settings.MODEL, 'fire.pt') # model path
model, pt, bs, imgsz, names, stride = load_model(weight_path, device, settings.DATA_COCO)
model2, pt2, bs2, imgsz2, names2, stride2 = load_model(weight_path2, device, settings.DATA_COCO)

input_image = 'datatest/images/ezviz.png' # original image path
input_image_path = 'datatest/images'
# for image_name in os.listdir(input_image_path):
    # input_image = input_image_path + '/' + image_name
image = cv2.imread(input_image)

# cv2.imwrite(input_image, image) # save original image
conf_thres = settings.CONF_THRES # confidence threshold
iou_thres = settings.IOU_THRES # NMS IOU threshold
# classified = get_detected_object(input_image, conf_thres, iou_thres, model, pt, bs, imgsz, names, stride, allow_classes=0)
classified1 = get_detected_object(input_image, conf_thres, iou_thres, model, pt, bs, imgsz, names, stride, json_object, allow_classes=2) # objects detection on image
classified2 = get_detected_object(input_image, conf_thres, iou_thres, model2, pt2, bs2, imgsz2, names2, stride2, json_object, allow_classes=1) # objects detection on image
time_tuple = time.localtime()
time_string = time.strftime('%d%m%Y%H%M%S')
classified = classified1 + classified2

print("classified",classified)
print("\n")
print("classified1",classified1)
print("\n")
print("classified2",classified2)
try:
    if len(classified) != 0:
        classified_overlap = check_overlap(classified, pts)      
        if len(classified_overlap) != 0:
            im_draw_detect_box = draw_warning_area(image, pts) # drawing detect bboxes
            # for i in range(len(classified_overlap)):
            #     if classified_overlap[i]['label'] == 'fire':
            #         classified_overlap[i]['label'] = 'Fire'
            im_show = draw_object_bboxes(im_draw_detect_box, classified_overlap, json_object) # drawing object bboxes
            output_image = f'datatest/results/detected_{time_string}.jpg'
            cv2.imwrite(output_image, im_show)

            # save image to use for train
            time_tuple = time.localtime()
            time_string = time.strftime('%Y%m%d_%H%M%S', time_tuple)
            data_image = '{}/{}.jpg'.format(settings.DATA_IMAGE_FOLDER, time_string)
            cv2.imwrite(data_image, im_show)      


            status, messages = get_message(classified_overlap, json_object)
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
import os
import sys
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))
import cv2
import json
from config import settings
from detect import get_detected_object
from utils.plots import draw_object_bboxes, draw_detect_bboxes

input_image_name = 'evn3.jpg'
input_image_path = f'./test/images/objects/{input_image_name}'
save_image_name = 'example.jpg'
save_image_path = f'./test/images/objects/{save_image_name}'

## pts of rectangle
# pts =[[128,250],[430,520]]
# pts = [[70,48],[525,273]]

## pts of polygon
# pts = [[102, 331], [307, 344], [279, 538], [49, 546]]

## pts of null
# pts = []


with open(os.path.join(os.getcwd(), 'info.json'), "r") as outfile:
    info_json = json.load(outfile)
    pts = info_json['coordinate']
print(pts)
image = cv2.imread(input_image_path)
device = '' # cuda device, i.e. 0 or 0,1,2,3 or cpu
weight_path = os.path.join(settings.MODEL, 'best.pt') # model path

classified, det, result, messages = get_detected_object(weight_path, device, settings.DATA_COCO, input_image_path, pts) # objects detection on image
im_draw_detect_box = draw_detect_bboxes(image, pts) # drawing detect bboxes
im_show = draw_object_bboxes(im_draw_detect_box, classified) # drawing object bboxes
# cv2.imwrite(save_image_path, im_show)
cv2.imshow('show', im_show)
cv2.waitKey(0)
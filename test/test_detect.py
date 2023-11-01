import os
import sys
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))

import cv2
import imutils
import time
import json
import numpy as np
from config import settings
from detect import get_detected_object
from PIL import ImageFont, ImageDraw, Image

number_of_colors = 5

def convert_name_id(eng_name, option):
    output = ''
    with open('object.json', 'r',encoding='utf-8') as outfile:
        json_object = json.load(outfile)
        for info in json_object['english_name']:
            try:
                if option == 'length_name':
                    output = info[eng_name][1]['length_name']
                elif option == 'ID':
                    output = info[eng_name][0]['ID']
                elif option == 'vietnamese_name':
                    output = info[eng_name][2]['vietnamese_name']                            
            except Exception:
                pass    
    
    return output

def draw_bboxes(im, classified, det):
    image_h, image_w, _ = im.shape
    bbox_thick = int(0.6 * (image_h + image_w) / 600)
    cv2_im_rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)# Convert the image to RGB (OpenCV uses BGR)
    pil_im = Image.fromarray(cv2_im_rgb)# Transform the cv2 image to PIL    
    font_object = ImageFont.truetype("arial.ttf", 18, encoding="unic")# Use a truetype font    
    draw = ImageDraw.Draw(pil_im)
    bbox_color = ['#008744', '#ab9c0c', '#8404ba', '#c98504', '#660513', '#77961b']# Colors of bounding box

    # Draw bbox on input image
    for info in classified:
        xmin = info['xmin']
        ymin = info['ymin']
        xmax = info['xmax']
        ymax = info['ymax']
        ID = convert_name_id(info['label'], 'ID')
        c1, c2 = (xmin, ymin), (xmax, ymax)
        draw.rectangle([c1, c2], outline = bbox_color[ID], width = 2)# Draw bbox on image

    # Draw bbox on input image
    for info in classified:
        xmin = info['xmin']
        ymin = info['ymin']
        xmax = info['xmax']
        ymax = info['ymax']
        ID = convert_name_id(info['label'], 'ID')
        c1, c2 = (xmin, ymin), (xmax, ymax)
        bbox_mess = '%s - %s' % (convert_name_id(info['label'], 'length_name'), info['score'])
        final_bbox_mess = '%s - %s' % (convert_name_id(info['label'], 'vietnamese_name'), info['score'])
        t_size = cv2.getTextSize(bbox_mess, 0, 0.5, thickness=bbox_thick // 2)[0]
        if ymin <= 10:
            draw.rectangle([(xmin, ymax), (xmin + t_size[0], ymax + 2*t_size[1])], fill = bbox_color[ID])# fill
            draw.text((xmin + 3, ymax), final_bbox_mess, font=font_object, fill=(255, 255, 255))# Draw the text on the image       
        else:
            draw.rectangle([(xmin, ymin - 2*t_size[1]), (xmin + t_size[0], ymin)], fill = bbox_color[ID])# fill
            draw.text((c1[0] + 3, c1[1] - 20), final_bbox_mess, font=font_object, fill=(255, 255, 255))# Draw the text on the image

    img = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)# Get back the image to OpenCV
    for i in range(len(classified)):
        info = classified[i]
        info2 = info.copy()
        info['label'] = convert_name_id(info2['label'], 'vietnamese_name')
    return img

input_image_name = 'evn5.jpg'
input_image_path = f'./test/images/objects/{input_image_name}'
image = cv2.imread(input_image_path)
device = '' # cuda device, i.e. 0 or 0,1,2,3 or cpu
weight_path = os.path.join(settings.MODEL, 'best2.pt') # model path
classified, det, result, messages = get_detected_object(weight_path, device, settings.DATA_COCO, input_image_path) # objects detection on image

print(classified)
if len(det) == 0:
    print("[INFO] No detected...")
    pass
else:
    im_show = draw_bboxes(image, classified, det)
    # cv2.imshow("IMG", imutils.resize(im_show, width=1400))
    cv2.imwrite(f'{input_image_name}', im_show)
    # cv2.waitKey(0)

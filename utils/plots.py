from pathlib import Path
import cv2
import numpy as np
import torch
from PIL import ImageFont, ImageDraw, Image
from utils.general import clip_boxes, increment_path, xywh2xyxy, xyxy2xywh

def save_one_box(xyxy, im, file=Path('im.jpg'), gain=1.02, pad=10, square=False, BGR=False, save=True):
    # Save image crop as {file} with crop size multiple {gain} and {pad} pixels. Save and/or return crop
    xyxy = torch.tensor(xyxy).view(-1, 4)
    b = xyxy2xywh(xyxy)  # boxes
    if square:
        b[:, 2:] = b[:, 2:].max(1)[0].unsqueeze(1)  # attempt rectangle to square
    b[:, 2:] = b[:, 2:] * gain + pad  # box wh * gain + pad
    xyxy = xywh2xyxy(b).long()
    clip_boxes(xyxy, im.shape)
    crop = im[int(xyxy[0, 1]):int(xyxy[0, 3]), int(xyxy[0, 0]):int(xyxy[0, 2]), ::(1 if BGR else -1)]
    if save:
        file.parent.mkdir(parents=True, exist_ok=True)  # make directory
        f = str(increment_path(file).with_suffix('.jpg'))
        # cv2.imwrite(f, crop)  # save BGR, https://github.com/ultralytics/yolov5/issues/7007 chroma subsampling issue
        Image.fromarray(crop[..., ::-1]).save(f, quality=95, subsampling=0)  # save RGB
    return crop


def convert_name_id(eng_name, option, json_object):
    output = ''
    for item in json_object["english_name"]:
        for key in item:
            if key == eng_name and option == 'length_name':
                output = item[key][0]["length_name"]
            elif key == eng_name and option == 'ID':
                output = item[key][0]["ID"]
            elif key == eng_name and option == 'vietnamese_name':
                output = item[key][0]["vietnamese_name"]
            elif key == eng_name and option == 'conf_thres':
                output = item[key][0]["conf_thres"]                          
    return output


def draw_object_bboxes(im, classified, json_object):
    image_h, image_w, _ = im.shape
    bbox_thick = int(0.6 * (image_h + image_w) / 400)
    cv2_im_rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB) # Convert the image to RGB (OpenCV uses BGR)
    pil_im = Image.fromarray(cv2_im_rgb) # Transform the cv2 image to PIL    
    font_object = ImageFont.truetype("arial.ttf", 18, encoding="unic") # Use a truetype font    
    draw = ImageDraw.Draw(pil_im)
    bbox_color = ['#e90b2b', '#696969', '#8404ba', '#ed9121', '#008000'] # Hexa colors of bounding box

    # Draw bbox on input image
    for info in classified:
        xmin = info['xmin']
        ymin = info['ymin']
        xmax = info['xmax']
        ymax = info['ymax']
        ID = convert_name_id(info['label'], 'ID', json_object)
        c1, c2 = (xmin, ymin), (xmax, ymax)
        draw.rectangle([c1, c2], outline = bbox_color[ID], width = bbox_thick)# Draw bbox on image

    # Draw information on bbox input image
    for info in classified:
        xmin = info['xmin']
        ymin = info['ymin']
        xmax = info['xmax']
        ymax = info['ymax']
        ID = convert_name_id(info['label'], 'ID', json_object)
        c1, c2 = (xmin, ymin), (xmax, ymax)
        object_score = float(info['score'])*100
        bbox_mess = '%s - %s' % (convert_name_id(info['label'], 'length_name', json_object), int(object_score)) + '%'
        final_bbox_mess = '%s - %s' % (convert_name_id(info['label'], 'vietnamese_name', json_object), int(object_score)) + '%'
        t_size = cv2.getTextSize(bbox_mess, 0, 0.5, thickness=bbox_thick // 2)[0]
        if ymin <= 10:
            draw.rectangle([(xmin, ymax), (xmin + t_size[0], ymax + 2*t_size[1])], fill = bbox_color[ID])# fill
            draw.text((xmin + 3, ymax), final_bbox_mess, font=font_object, fill=(255, 255, 255))# Draw the text on the image       
        else:
            draw.rectangle([(xmin, ymin - 2*t_size[1]), (xmin + t_size[0], ymin)], fill = bbox_color[ID])# fill
            draw.text((c1[0] + 3, c1[1] - 20), final_bbox_mess, font=font_object, fill=(255, 255, 255))# Draw the text on the image
        
    img = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)# Get back the image to OpenCV

    return img

# Draw the warning area on the image
def draw_warning_area(im, pts):
    image_h, image_w, _ = im.shape
    bbox_thick = int(0.6 * (image_h + image_w) / 600)
    if len(pts) >= 3:    
        cv2.polylines(im, np.array([pts], np.int32), True, (235, 84, 47), bbox_thick) # BGR
    elif len(pts) == 2:
        start_point = pts[0]
        end_point = pts[1]
        x0 = start_point[0]
        y0 = start_point[1]
        x1 = end_point[0]
        y1 = end_point[1] 
        cv2.rectangle(im, (x0, y0), (x1, y1), (235, 84, 47), bbox_thick) # BGR
    elif len(pts) == 0:
        pass

    return im

def information(classified, json_object):
    for i in range(len(classified)):
        info = classified[i]
        info2 = info.copy()
        info['label_EN'] = info2['label']
        info['label'] = convert_name_id(info2['label'], 'vietnamese_name', json_object)

    return classified
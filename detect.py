import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
import sys
import torch
import numpy as np
from pathlib import Path
import torch.backends.cudnn as cudnn

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from models.common import DetectMultiBackend
from utils.dataloaders import LoadImages
from utils.general import (LOGGER, Profile, check_img_size, non_max_suppression, scale_boxes)
from utils.torch_utils import select_device, smart_inference_mode
from utils.plots import convert_name_id
@smart_inference_mode()

def xywh2xyxy(x):
    # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y[..., 0] = x[..., 0] - x[..., 2] / 2  # top left x
    y[..., 1] = x[..., 1] - x[..., 3] / 2  # top left y
    y[..., 2] = x[..., 0] + x[..., 2] / 2  # bottom right x
    y[..., 3] = x[..., 1] + x[..., 3] / 2  # bottom right y
    return y


def clip_boxes(boxes, shape):
    # Clip boxes (xyxy) to image shape (height, width)
    if isinstance(boxes, torch.Tensor):  # faster individually
        boxes[..., 0].clamp_(0, shape[1])  # x1
        boxes[..., 1].clamp_(0, shape[0])  # y1
        boxes[..., 2].clamp_(0, shape[1])  # x2
        boxes[..., 3].clamp_(0, shape[0])  # y2
    else:  # np.array (faster grouped)
        boxes[..., [0, 2]] = boxes[..., [0, 2]].clip(0, shape[1])  # x1, x2
        boxes[..., [1, 3]] = boxes[..., [1, 3]].clip(0, shape[0])  # y1, y2

# Load model
def load_model(weights, device, data):
    data = str(ROOT / data)
    weights = str(ROOT / weights)
    device = select_device(device)
    imgsz=(640, 640) # inference size (height, width)
    model = DetectMultiBackend(weights, device=device, dnn=False, data=data, fp16=False)
    stride, names, pt = model.stride, model.names, model.pt
    imgsz = check_img_size(imgsz, s=stride)  # check image size
    bs = 1  # batch_size
    
    return model, pt, bs, imgsz, names, stride

# Detect object
def get_detected_object_v5(source, conf_thres, iou_thres, model, pt, bs, imgsz, names, stride, json_object, allow_classes):
    if allow_classes == 1: # Smoke Vehicle Kite Tree
        classes = [1, 2, 3, 4] # filter by class: --class 0, or --class 0 2 3
    elif allow_classes == 2: # Fire
        classes = [0]
    elif allow_classes == 0: # All
        classes = None
    classified = []
    imgsz = (640, 640)  # inference size (height, width)
    max_det = 10  # maximum detections per image
    
    agnostic_nms = False # class-agnostic NMS

    dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt)

    # Run inference
    model.warmup(imgsz=(1 if pt or model.triton else bs, 3, *imgsz))  # warmup
    _, _, dt = 0, [], (Profile(), Profile(), Profile())
    for _, im, im0s, _, _ in dataset:
        with dt[0]:
            im = torch.from_numpy(im).to(model.device)
            im = im.half() if model.fp16 else im.float()  # uint8 to fp16/32
            im /= 255  # 0 - 255 to 0.0 - 1.0
            if len(im.shape) == 3:
                im = im[None]  # expand for batch dim

        # Inference
        with dt[1]:
            pred = model(im, augment=False, visualize=False)

        # NMS
        with dt[2]:
            pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)

        # Process predictions
        for _, det in enumerate(pred):  # per image
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0s.shape).round()

                # Get results
                for *xyxy, conf, cls in reversed(det):
                    c = int(cls)  # integer class                  
                    if not isinstance(xyxy, torch.Tensor):  # may be list
                        xyxy = torch.stack(xyxy)

                    conf_thres = convert_name_id(names[c].capitalize(), 'conf_thres', json_object) # threshold we define
                    detect_conf = f'{conf:.2f}' # threshold model predict
                    if float(detect_conf) >= float(conf_thres):
                        doc = {
                            'xmin': int(xyxy[0]), 
                            'ymin': int(xyxy[1]), 
                            'xmax': int(xyxy[2]), 
                            'ymax': int(xyxy[3]), 
                            'score': f'{conf:.2f}',
                            'label': names[c].capitalize()
                        }
                        classified.append(doc)

    return classified

# def get_detected_object_v8(source, conf_thres, iou_thres, model, imgsz, stride, json_object):
#     classified = []
#     imgsz = (640, 640)  # inference size (height, width)
#     max_det = 10  # maximum detections per image
#     agnostic_nms = False # class-agnostic NMS

#     # Run inference
#     results = model.predict(source, imgsz = imgsz, conf = conf_thres, iou = iou_thres,\
#                             max_det = max_det, agnostic_nms = agnostic_nms, vid_stride = stride)
#     names = model.names

#     # Process results list
#     for result in results:
#         boxes = result.boxes  # Boxes object for bounding box outputs
#         cls = boxes.cls
#         conf = boxes.conf  # Confidence level
#         xyxys = boxes.xyxy.tolist()

#         for xyxy, conf, cls in zip(xyxys, conf, cls):
#             c = int(cls)  # integer class  
#             conf_thres = convert_name_id(names[c].capitalize(), 'conf_thres', json_object) # threshold we define
#             detect_conf = f'{conf:.2f}' # threshold model predict
#             if float(detect_conf) >= float(conf_thres):               
#                 doc = {
#                     'xmin': int(xyxy[0]), 
#                     'ymin': int(xyxy[1]), 
#                     'xmax': int(xyxy[2]), 
#                     'ymax': int(xyxy[3]), 
#                     'score': f'{conf:.2f}',
#                     'label': names[c].capitalize()
#                 }                 
#                 classified.append(doc)

#     return classified
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

from utils.torch_utils import smart_inference_mode
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


def get_detected_object_v8(source, conf_thres, iou_thres, model, json_object):
    classified = []
    imgsz = (640, 640)  # inference size (height, width)
    stride = 1
    max_det = 10  # maximum detections per image
    agnostic_nms = False # class-agnostic NMS

    # Run inference
    results = model.predict(source, imgsz = imgsz, conf = conf_thres, iou = iou_thres,\
                            max_det = max_det, agnostic_nms = agnostic_nms, vid_stride = stride)
    names = model.names

    # Process results list
    for result in results:
        boxes = result.boxes  # Boxes object for bounding box outputs
        cls = boxes.cls
        conf = boxes.conf  # Confidence level
        xyxys = boxes.xyxy.tolist()

        for xyxy, conf, cls in zip(xyxys, conf, cls):
            c = int(cls)  # integer class  
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
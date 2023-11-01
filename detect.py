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
def load_model(weights, device, data, source):
    data = str(ROOT / data)
    weights = str(ROOT / weights)
    device = select_device(device)
    imgsz=(640, 640) # inference size (height, width)
    model = DetectMultiBackend(weights, device=device, dnn=False, data=data, fp16=False)
    stride, names, pt = model.stride, model.names, model.pt
    imgsz = check_img_size(imgsz, s=stride)  # check image size
    dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt)
    bs = 1  # batch_size
    return model, pt, bs, imgsz, dataset, device, names

# Detect object
def get_detected_object(weights, device, data, source):
    classified = []
    result = []
    messages = []
    imgsz = (640, 640)  # inference size (height, width)
    conf_thres = 0.35  # confidence threshold
    iou_thres = 0.55  # NMS IOU threshold
    max_det = 1000  # maximum detections per image
    classes = None # filter by class: --class 0, or --class 0 2 3
    agnostic_nms = False # class-agnostic NMS

    model, pt, bs, imgsz, dataset, device, names = load_model(weights, device, data, source)

    # Run inference
    model.warmup(imgsz=(1 if pt or model.triton else bs, 3, *imgsz))  # warmup
    seen, _, dt = 0, [], (Profile(), Profile(), Profile())
    for path, im, im0s, _, s in dataset:
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
        for i, det in enumerate(pred):  # per image
            seen += 1
            p, im0, _ = path, im0s.copy(), getattr(dataset, 'frame', 0)
            p = Path(p)  # to Path
            s += '%gx%g ' % im.shape[2:]  # print string
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()

                for c in det[:, 5].unique():
                    n = (det[:, 5] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string
                    name_label = f"{names[int(c)]}"
                    numbers_label = f"{n}"
                    info_label = {
                        "label": name_label,
                        "numbers": numbers_label
                    }
                    vn_label = convert_name_id(name_label, 'vietnamese_name')
                    object_mess = f"Phát hiện {numbers_label} {vn_label}."
                    messages.append(object_mess)                    
                    result.append(info_label)

                # Get results
                for *xyxy, conf, cls in reversed(det):
                    c = int(cls)  # integer class                  
                    if not isinstance(xyxy, torch.Tensor):  # may be list
                        xyxy = torch.stack(xyxy)
                    doc = {
                        'xmin': int(xyxy[0]), 
                        'ymin': int(xyxy[1]), 
                        'xmax': int(xyxy[2]), 
                        'ymax': int(xyxy[3]), 
                        'score': f'{conf:.2f}',
                        'label': names[c]
                   }                 
                    classified.append(doc)
    # Print results
    t = tuple(x.t / seen * 1E3 for x in dt)  # speeds per image
    LOGGER.info(f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS per image at shape {(1, 3, *imgsz)}' % t)
    return classified, det, result, messages

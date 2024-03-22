import os
import sys
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))
import cv2
from matplotlib import colors
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors


# model = YOLO("resources/weight_init/best.pt", "detect")
def get_detected_object(source, conf_thres, iou_thres, model, imgsz, stride):
    classified = []
    imgsz = (640, 640)  # inference size (height, width)
    max_det = 10  # maximum detections per image
    classes = None # filter by class: --class 0, or --class 0 2 3
    agnostic_nms = False # class-agnostic NMS


    # Run inference
    results = model.predict(source, imgsz = imgsz, conf = conf_thres, iou = iou_thres,\
                            max_det = max_det, agnostic_nms = agnostic_nms, vid_stride = stride, stream=True)
    names = model.names
    # return a list of Results objects
    # im0 = results.orig_img
    # names = results.names
    # Process results list
    for result in results:
        # print("[INFO]",result.boxes)
        boxes = result.boxes  # Boxes object for bounding box outputs
        cls = boxes.cls
        conf = boxes.conf  # Confidence level
        xyxys = boxes.xyxy.tolist()
        annotator = Annotator(result.orig_img, line_width=2, example=str(names))
        for xyxy, conf, cls in zip(xyxys, conf, cls):
            c = int(cls)  # integer class  
            print(xyxy)                
            doc = {
                'xmin': int(xyxy[0]), 
                'ymin': int(xyxy[1]), 
                'xmax': int(xyxy[2]), 
                'ymax': int(xyxy[3]), 
                'score': f'{conf:.2f}',
                'label': names[c]
            }                 
            classified.append(doc)
            label = f"{names[c]}  {conf:.2f}"
            annotator.box_label(xyxy,  label, color=colors(c, True))
        cv2.waitKey(1)
        im = annotator.result()
        cv2.imshow("Test", im)
        cv2.waitKey(1)
    return classified

model = YOLO("resources/weight_init/fire.pt", "detect")
path = "datatest/images/ezviz.png"
vid_path = "data/videos/J52222411_1_videocut_1710749241.mp4"
image = cv2.imread(vid_path)
x = get_detected_object(image, 0.5, 0.5, model, 640, 1)
print(x)
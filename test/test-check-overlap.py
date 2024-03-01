import os
import sys 
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(WORKING_DIR, "../"))
import cv2
import numpy as np
import json
from shapely.geometry import Polygon

with open(os.path.join(os.getcwd(), 'info.json'), "r") as outfile:
    info_json = json.load(outfile)
    PTS_POLYGON = info_json['coordinate']
PTS_POLYGON2 = [
          [
               10,
               10
          ],
          [
               100,
               100
          ]
     ]
xmin = PTS_POLYGON2[0][0]
xmax = PTS_POLYGON2[1][0]
ymin = PTS_POLYGON2[0][1]
ymax = PTS_POLYGON2[1][1]

PTS_POLYGON2 = [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]]

image_path = 'test/images/objects/original.jpg'

image = cv2.imread(image_path)
print(image.shape)
isClosed = True

pts1 = np.array(PTS_POLYGON, np.int32)
pts2 = np.array(PTS_POLYGON2, np.int32)
mask = cv2.polylines(image, [pts1], isClosed, (255, 0, 0), 2)
mask2 = cv2.polylines(mask, [pts2], isClosed, (0, 0, 255), 2)
# mask2 = cv2.rectangle(mask, PTS_POLYGON2[0], PTS_POLYGON2[1], (0, 255, 0), 2)
polygon1 = Polygon(PTS_POLYGON)
polygon2 = Polygon(PTS_POLYGON2)
intersect = polygon1.intersection(polygon2).area
union = polygon1.union(polygon2).area
iou = intersect / union
print(iou)

cv2.imshow('IMG', cv2.resize(mask2, (1080, 720)))
cv2.waitKey(0)
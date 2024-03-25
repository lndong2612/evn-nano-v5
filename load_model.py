import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
import sys
from pathlib import Path
from models.common import DetectMultiBackend
from utils.torch_utils import select_device
from utils.general import check_img_size

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

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
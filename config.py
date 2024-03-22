import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    HOST: str = '0.0.0.0'
    PORT: int = 9298
    URLSV = 'https://tcamera.thinklabs.com.vn/api'
    API_V1_STR: str = "/detect_object"
    RESOURCES: str = './resources'
    IMAGE_FOLDER: str = os.path.join(RESOURCES, 'images')
    DATA_IMAGE_FOLDER: str = os.path.join(RESOURCES, 'data')
    MODEL: str = os.path.join(RESOURCES, 'weight_init')
    DATA_COCO: str = './data/coco.yaml'
    CONF_THRES: float = 0 # confidence threshold
    IOU_THRES: float = 0.65 # NMS IOU threshold
    FRAME_RATE: int = 1 # Frame per second
    OPTION: int = 2 # 1: Using 1 Model; 2: Using 2 Model

settings = Settings()
settings.IMAGE_FOLDER: str = os.path.join(settings.RESOURCES, 'images')
settings.DATA_IMAGE_FOLDER: str = os.path.join(settings.RESOURCES, 'data')
settings.MODEL: str = os.path.join(settings.RESOURCES, 'weight_init')
settings.DATA_COCO: str = settings.DATA_COCO
settings.URLSV: str = settings.URLSV

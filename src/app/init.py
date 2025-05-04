import cv2
import torch
from ultralytics import YOLO
from torchvision import transforms
from PIL import Image
import numpy as np
import torch.nn.functional as F


import os


from src.features.detection import DroneDetectionFactory
from src.features.classification import IDroneClassification, DroneClassificationFactory
from src.features.load_video import LoadVideoFactory

from .app import DroneDetectionPipeline

from src.features.analyzer import VideoAnalyzer


YOLO_NAME = "best.pt"
MOBILE_NET_NAME = "resnet18_bpla-21-04-2025-13_45.pth"

current_dir = os.path.dirname(__file__)

yolo_path = os.path.join(current_dir, "models", "yolo", YOLO_NAME)
mobile_net_path = os.path.join(current_dir, "models", "mobilenet", MOBILE_NET_NAME)

for file in [yolo_path, mobile_net_path]:
    if not os.path.exists(file):
        raise FileNotFoundError(file)

YOLO_MODEL = YOLO(yolo_path)

MOBILENET_MODEL = torch.load(mobile_net_path, map_location=torch.device("cpu"))
MOBILENET_MODEL.eval()


drone_detection = DroneDetectionFactory.create(YOLO_MODEL)
drone_classification_detection = DroneClassificationFactory.create(MOBILENET_MODEL)

video_analyzer = VideoAnalyzer()

load_video = LoadVideoFactory.create()

pipeline = DroneDetectionPipeline(
    drone_detection, drone_classification_detection, load_video, video_analyzer
)


import os

paths = [
    "/tmp/drones/rows/",
    "/tmp/drones/reports/",
    "/tmp/drones/processed/"
]

for path in paths:
    os.makedirs(path, exist_ok=True)

print("Папки успешно созданы.")

from .services import IDroneDetection, YOLOv8DroneDetection
from ultralytics import YOLO

class DroneDetectionFactory:

    @staticmethod
    def create(model: YOLO) -> IDroneDetection:
        return YOLOv8DroneDetection(model)

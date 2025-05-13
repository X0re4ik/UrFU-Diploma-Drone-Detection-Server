from .services import IDroneDetection, YOLOv8DroneDetection, YOLOv8DroneDetectionWithTracker
from ultralytics import YOLO

class DroneDetectionFactory:

    @staticmethod
    def create(model: YOLO) -> IDroneDetection:
        return YOLOv8DroneDetection(model)



class DroneDetectionWithTrackerFactory:

    @staticmethod
    def create(model: YOLO, tracker_path: str) -> IDroneDetection:
        return YOLOv8DroneDetectionWithTracker(model, tracker_path)

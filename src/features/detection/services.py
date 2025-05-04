from abc import ABC
from ultralytics import YOLO
import os

from src.shared.typing import FrameType

from ultralytics import YOLO


from src.entity.drone_box import DroneBoxDTO

class IDroneDetection(ABC):

    def get_drone_bbox(self, frame: FrameType) -> list[DroneBoxDTO]:
        """"""


class YOLOv8DroneDetection(IDroneDetection):

    def __init__(self, model: YOLO, conf: float = 0.5):
        self._model = model
        self._conf = conf

    def get_drone_bbox(self, frame: FrameType) -> list[DroneBoxDTO]:
        results = self._model(frame)[0]

        detections_results: list[DroneBoxDTO] = []
        for box, conf, cls in zip(
            results.boxes.xyxy, results.boxes.conf, results.boxes.cls
        ):
            xmin, ymin, xmax, ymax = map(int, box[:4].tolist())
            if conf < self._conf:
                continue

            detections_results.append(
                DroneBoxDTO([xmin, ymin, xmax, ymax], conf.item(), "Aircraft-Type-UAV")
            )
        return detections_results

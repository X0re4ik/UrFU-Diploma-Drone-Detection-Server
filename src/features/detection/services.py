from collections import defaultdict


from typing import Any
from PIL import Image


import cv2
import torch
from torchvision import transforms
from PIL import Image
import numpy as np
import torch.nn.functional as F


import cv2
import numpy as np

from ultralytics import YOLO

from abc import ABC
from ultralytics import YOLO
import os
from collections import defaultdict


from src.shared.typing import FrameType

from ultralytics import YOLO


from src.entity.drone_box import DroneBoxDTO


CLASSES = ["БПЛА", "Квадракоптер", "Птица", "Самолет"]


class IDroneDetection(ABC):

    def get_track_history(self, track_id: int) -> list[tuple[float], tuple[float]]:
        """"""

    def get_drone_bbox(self, frame: FrameType) -> list[DroneBoxDTO]:
        """"""


class YOLOv8DroneDetection(IDroneDetection):

    def __init__(self, model: YOLO, conf: float = 0.5):
        self._model = model
        self._conf = conf

    def get_track_history(self, track_id: int) -> list[tuple[float], tuple[float]]:
        return []

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
                DroneBoxDTO(
                    [xmin, ymin, xmax, ymax], conf.item(), CLASSES[int(cls.item())]
                )
            )

        return detections_results


class YOLOv8DroneDetectionWithTracker(IDroneDetection):

    def __init__(self, model: YOLO, trakcer_yaml: str, conf: float = 0.4):
        self._model = model
        self._conf = conf
        self._trakcer_yaml = trakcer_yaml

        if not os.path.exists(self._trakcer_yaml):
            raise FileNotFoundError(trakcer_yaml)

        self._tracker_history = defaultdict(list)

        self._max_tracker_detection = 1000

    def get_track_history(self, track_id: int) -> list[tuple[float], tuple[float]]:
        return self._tracker_history[track_id]

    def get_drone_bbox(self, frame: FrameType) -> list[DroneBoxDTO]:
        result = self._model.track(frame, persist=True, tracker=self._trakcer_yaml, verbose=False)[0]

        if not result.boxes or result.boxes.id is None:
            return []

        detections_results: list[DroneBoxDTO] = []

        boxes = result.boxes.xywh.cpu()
        confs = result.boxes.conf.cpu()
        clses = result.boxes.cls.cpu()
        track_ids = result.boxes.id.int().cpu().tolist()

        for box, track_id, conf, cls in zip(boxes, track_ids, confs, clses):

            class_id = int(cls.item())
            conf = float(conf.item())

            if conf < self._conf:
                continue

            x, y, w, h = box
            track = self._tracker_history[track_id]
            track.append((float(x), float(y)))  # x, y center point
            if (
                len(track) > self._max_tracker_detection
            ):  # retain 30 tracks for 30 frames
                track.pop(0)

            xmin, ymin, xmax, ymax = (
                int(x - w / 2),
                int(y - h / 2),
                int(x + w / 2),
                int(y + h / 2),
            )

            detections_results.append(
                DroneBoxDTO(
                    [xmin, ymin, xmax, ymax], conf, CLASSES[class_id], track_id
                )
            )

        return detections_results

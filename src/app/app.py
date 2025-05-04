import time
from typing import Any
import cv2

from src.features.analyzer.services import VideoAnalyzer, save_plot_to_bytes

from src.features.detection import IDroneDetection
from src.features.classification import IDroneClassification

from src.entity.statistics import (
    DroneDetectionStatisticsDTO,
    DroneModelStatisticsDTO,
)

from src.features.download_video.services import get_download_video
from src.features.load_report.services import LoadReport, get_report
from src.features.load_video import ILoadVideo


from src.shared.typing import FrameType


import logging


logger = logging.getLogger(__name__)


class DroneDetectionPipeline:

    def __init__(
        self,
        drone_detection: IDroneDetection,
        drone_classification: IDroneClassification,
        load_video: ILoadVideo,
        statistics: VideoAnalyzer,
        *,
        cv2_show: bool = True,
    ):
        self._drone_detection = drone_detection
        self._drone_classification = drone_classification
        self._load_video = load_video

        self._statistics = statistics

        self._cv2_show = cv2_show

    def detect(self, unique_id: str):
        
        logger.info(f"Получил объект на обработку: {unique_id}")

        #path_to_file: str = self._load_video.download(unique_id)

        cap = cv2.VideoCapture("/home/anton/X0re4ik/UrFU/app/server/drone-detection-server/dev/examples/5.mp4")
        
        if not cap.isOpened():
            raise Exception()

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fps = cap.get(cv2.CAP_PROP_FPS)
        out = cv2.VideoWriter(
            f"/tmp/drones/processed/{unique_id}.mp4",
            fourcc,
            fps,
            (
                int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            ),
        )

        frame_id = 0

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        self._statistics.set_video_info(total_frames, fps)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            magic_boxes = self._drone_detection.get_drone_bbox(frame)

            for magic_box in magic_boxes:
                xmin, ymin, xmax, ymax = magic_box.bbox

                logger.info(
                    f"Detect: {[xmin, ymin, xmax, ymax]} | {magic_box.model_id}"
                )

                if magic_box.model_id == "Aircraft-Type-UAV":
                    cropped = frame[ymin:ymax, xmin:xmax]
                    if cropped.size == 0:
                        continue

                    drone_type_info = self._drone_classification.get_class(cropped)

                    cv2.putText(
                        frame,
                        drone_type_info.model_id,
                        (xmin, ymax + 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.3,
                        (255, 0, 0),
                        1,
                    )
                    drone_model_statistics = DroneModelStatisticsDTO(
                        drone_type_info.confidence, drone_type_info.model_id
                    )
                    self._statistics.update_model_statistics(
                        frame_id, drone_model_statistics
                    )

                if magic_box.model_id == "Quadcopter-Type-UAV":
                    pass

                self._statistics.update_drone_detection(
                    frame_id,
                    DroneDetectionStatisticsDTO(
                        magic_box.confidence, magic_box.model_id
                    ),
                )
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 0, 255), 2)
                cv2.putText(
                    frame,
                    magic_box.model_id,
                    (xmin, ymin - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    (0, 0, 255),
                    1,
                )

            if self._cv2_show:
                cv2.imshow("Video DroneDetection", frame)
                if cv2.waitKey(25) & 0xFF == ord("q"):
                    break

            frame_id += 1
            out.write(frame)

        cap.release()
        out.release()

        cv2.destroyAllWindows()

        report_folder = get_report().save_report(self._statistics.report(), f"{unique_id}.png")

        detection_video_folder = get_download_video().download(f"/tmp/drones/processed/{unique_id}.mp4")

        return {
            "model_percent": self._statistics.get_model_percent(),
            "type_percent": self._statistics.get_type_percent(),
            "report": report_folder,
            "detection_video": detection_video_folder,
        }

    def get_statisticts(self):
        return self._statistics

from typing import Literal
import cv2
import time


from dataclasses import dataclass
from typing import Literal, List, Dict
from collections import defaultdict
import torch
import numpy as np
import matplotlib.pyplot as plt

from dataclasses import dataclass

import numpy as np

from src.entity.statistics import (
    DroneDetectionStatisticsDTO,
    DroneModelStatisticsDTO,
)

from collections import defaultdict


import io
import matplotlib.pyplot as plt
from typing import Tuple


def save_plot_to_bytes(fig: plt.Figure) -> Tuple[bytes, str]:
    """
    Сохраняет график в байты и возвращает расширение файла

    Args:
        fig: Фигура matplotlib

    Returns:
        Tuple[bytes, str]: Байты изображения и расширение файла (например, 'png')
    """
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight", dpi=150)
    buffer.seek(0)
    return buffer.getvalue(), "png"


def draw_bar(ax, x, y, colors, title, xlabel, ylabel, annotations=None):
    """Универсальная функция для отрисовки столбцов"""
    bars = ax.bar(x, y, color=colors, width=0.6)
    ax.set_title(title, fontsize=12)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.7)


class VideoAnalyzer:
    def __init__(self):
        self._drone_detection_statistics = defaultdict(
            list[DroneDetectionStatisticsDTO]
        )
        self._drone_model_statistics = defaultdict(list[DroneModelStatisticsDTO])

    def set_video_info(self, total_frames: int, fps: int) -> None:
        self.total_frames = total_frames
        self.fps = fps
        self.video_time_sec = total_frames / fps

    def update_drone_detection(
        self,
        frame_id: int,
        drone_detection: DroneDetectionStatisticsDTO,
    ) -> None:
        self._drone_detection_statistics[frame_id].append(drone_detection)

    def update_model_statistics(
        self, frame_id: int, drone_model: DroneModelStatisticsDTO
    ) -> None:
        self._drone_model_statistics[frame_id].append(drone_model)

    def get_model_percent(self) -> tuple[str, int, int] | None:
        if len(self._drone_model_statistics) == 0:
            return None

        model_stats = defaultdict(float)

        for _, model_list in self._drone_model_statistics.items():
            for model in model_list:
                model_name = model.model_id
                model_stats[model_name] += 1

        max_count = 0
        max_count_model = None
        for model, count in model_stats.items():
            if count > max_count:
                max_count_model = model
                max_count = count

        assert max_count_model, max_count_model

        return max_count_model, max_count, (max_count / self.total_frames) * 100

    def get_average_confidence_in_model(self, model: str) -> float:
        average_confidence: float = 0.0
        count_models = 0
        for _, model_list in self._drone_model_statistics.items():
            for model_ in model_list:
                model_name = model_.model_id
                if model_name == model:
                    average_confidence += 1
                    count_models +=1

        if count_models == 0:
            return 0
        
        return average_confidence / count_models

    def get_type_percent(self) -> tuple[str, int, int] | None:
        if len(self._drone_detection_statistics) == 0:
            return None

        type_stats = defaultdict(int)
        # Анализ обнаружений
        for _, detection_list in self._drone_detection_statistics.items():
            for detection in detection_list:
                drone_type = detection.class_id
                type_stats[drone_type] += 1
        max_count = 0
        max_count_type = None
        for type_, count in type_stats.items():
            if count > max_count:
                max_count_type = type_
                max_count = count

        assert max_count_type, max_count_type

        return type_, max_count, (max_count / self.total_frames) * 100

    def get_models_with_type(self) -> list[tuple[str, int]]:
        model_stats = defaultdict(int)
        for _, model_list in self._drone_model_statistics.items():
            for model in model_list:
                model_name = model.model_id
                model_stats[model_name] += 1

        return list(model_stats.items())

    def get_frames_lines(self) -> list[int]:
        return np.linspace(0, self.total_frames, self.total_frames)

    def distribution_of_types_lines(self) -> list[str | None]:
        """
        Распредление типов БПЛА
        """
        distribution_of_types = []
        for frame_id in range(self.total_frames):
            drone_model = self._drone_model_statistics.get(frame_id, None)
            model = None
            if drone_model:
                model = drone_model[0].model_id
            distribution_of_types.append(model)
        return distribution_of_types

    def drone_confidences_lines(self) -> list[int]:
        """
        Распределение уверенности в детекции БПЛА
        """
        drone_confidences = []
        for frame_id in range(self.total_frames):
            drone_detection = self._drone_detection_statistics.get(frame_id, None)
            drone_conf = 0
            if drone_detection:
                drone_conf = drone_detection[0].confidence
            drone_confidences.append(drone_conf)
        return drone_confidences

    def model_confidences_lines(self) -> list[int]:
        """
        Распределение уверенности в модели БПЛА
        """
        model_confidences = []
        for frame_id in range(self.total_frames):
            model_detection = self._drone_model_statistics.get(frame_id, None)
            drone_conf = 0
            if model_detection:
                drone_conf = model_detection[0].confidence
            model_confidences.append(drone_conf)
        return model_confidences

    def total_count_lines(self) -> list[int]:
        count_drones = []
        for frame_id in range(self.total_frames):
            dd = self._drone_detection_statistics.get(frame_id, None)
            count_drone = 0
            if dd:
                count_drone = len(dd)
            count_drones.append(count_drone)
        return count_drone

    def report(self) -> plt.Figure:

        fig, axs = plt.subplots(2, 2, figsize=(15, 10))
        frames_lines = self.get_frames_lines()
        drone_confidences_lines = self.drone_confidences_lines()
        model_confidences_lines = self.model_confidences_lines()
        total_count_lines = self.total_count_lines()

        models_with_type = self.get_models_with_type()

        draw_bar(
            axs[0, 0],
            frames_lines,
            drone_confidences_lines,
            "skyblue",
            "Уверенность обнаружения",
            "Номер кадра",
            "Уверенность",
            [],
        )

        draw_bar(
            axs[0, 1],
            frames_lines,
            model_confidences_lines,
            ["red"],
            "Уверенность модели",
            "Номер кадра",
            "Уверенность",
            [],
        )

        draw_bar(
            axs[1, 0],
            [model for (model, _) in models_with_type],
            [count for (_, count) in models_with_type],
            "lightgreen",
            "Количество дронов",
            "Номер кадра",
            "Количество",
            [],
        )

        draw_bar(
            axs[1, 1],
            frames_lines,
            total_count_lines,
            "lightgreen",
            "Количество дронов",
            "Номер кадра",
            "Количество",
            [],
        )

        return fig

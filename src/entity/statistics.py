from dataclasses import dataclass
from typing import Literal

from src.shared.typing import DroneClassIDType, DroneModelIDType


@dataclass
class DroneDetectionStatisticsDTO:
    confidence: float
    class_id: DroneClassIDType


@dataclass
class DroneModelStatisticsDTO:
    confidence: float
    model_id: DroneModelIDType

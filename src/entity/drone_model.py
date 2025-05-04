from dataclasses import dataclass

from src.shared.typing import DroneModelIDType




@dataclass
class DroneModelDTO:
    confidence: float
    model_id: DroneModelIDType
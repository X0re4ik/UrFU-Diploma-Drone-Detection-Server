from dataclasses import dataclass

from src.shared.typing import DroneClassIDType



@dataclass
class DroneBoxDTO:
    bbox: list[int]
    confidence: float
    model_id: DroneClassIDType

    def __post_init__(self):
        if len(self.bbox) != 4:
            raise ValueError(
                "bounding_box должен состоять из [top(y1), left(x1), bottom(y2), right(x2)]"
            )

        if self.confidence > 1.0 or self.confidence < 0:
            raise ValueError(
                f"Уверенность не может должна быть 0 < confidence ({self.confidence}) < 1"
            )


from dataclasses import dataclass

from typing import Literal


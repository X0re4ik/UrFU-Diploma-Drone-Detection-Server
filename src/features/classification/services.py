from typing import Any
from src.shared.typing import FrameType
from PIL import Image

from src.entity.drone_model import DroneModelDTO

import cv2
import torch
from torchvision import transforms
from PIL import Image
import numpy as np
import torch.nn.functional as F


CLASSES = [
    "A22 Foxbat",
    "Bayraktar TB2",
    "UJ-22 Airborne",
]


class IDroneClassification:

    def get_class(self, frame: FrameType) -> DroneModelDTO | None:
        """_summary_

        Args:
            frame (FrameType): _description_

        Returns:
            DroneTypeInfo | None: _description_
        """


class DroneClassification(IDroneClassification):

    def __init__(self, transform: transforms.Compose, model: Any):
        self._transform = transform
        self._model = model

    def get_class(self, frame: FrameType) -> DroneModelDTO | None:

        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        input_tensor = self._transform(pil_image).unsqueeze(0)

        with torch.no_grad():
            logits = self._model(input_tensor)
            probs = F.softmax(logits, dim=1)
            confidence, predicted_class = torch.max(probs, dim=1)
        confidence = float(confidence.numpy()[0])
        return DroneModelDTO(confidence, CLASSES[predicted_class])

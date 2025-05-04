from typing import Any
from torchvision import transforms
from .services import DroneClassification, IDroneClassification


TRANSFORMS = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)

class DroneClassificationFactory:

    @staticmethod
    def create(model: Any) -> IDroneClassification:
        return DroneClassification(TRANSFORMS, model)

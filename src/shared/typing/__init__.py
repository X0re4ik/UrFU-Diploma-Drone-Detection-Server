import cv2
import numpy
from typing import Literal, Callable, Union


FrameType = cv2.typing.MatLike
DroneClassIDType = Literal["БПЛА", "Квадракоптер", "Птица", "Самолет"]
DroneModelIDType = Literal["A22 Foxbat", "Bayraktar TB2", "UJ-22 Airborne", "Unknown"]

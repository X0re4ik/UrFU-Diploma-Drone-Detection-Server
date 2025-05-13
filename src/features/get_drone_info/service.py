from dataclasses import dataclass

import os


import json


@dataclass
class DroneInfoDTO:
    model_name: str
    maximum_payload: float
    maximum_speed: float
    cruising_speed: float
    communication_range: float
    photo: bytes


class GetDroneInfo:

    def __init__(self):
        self._path_to_info = os.path.join(os.path.dirname(__file__), "db", "info.json")

        if not os.path.exists(self._path_to_info):
            raise FileNotFoundError(self._path_to_info)

        self._image_dir = os.path.join(
            os.path.dirname(__file__),
            "db",
            "images",
        )

        if not os.path.isdir(self._image_dir):
            raise Exception(self._image_dir)

    def get_frone_info(self, model_id: str) -> DroneInfoDTO:

        with open(self._path_to_info, "r") as json_file:
            dict_data = json.loads(json_file.read())

        for data in dict_data:
            if data["modelName"] == model_id:
                path_to_image = os.path.join(self._image_dir, data["photo"])

                with open(path_to_image, "rb") as photo:
                    return DroneInfoDTO(
                        data["modelName"],
                        data["maximumPayload"],
                        data["maximumSpeed"],
                        data["cruisingSpeed"],
                        data["communicationRange"],
                        photo.read(),
                    )

        raise Exception()

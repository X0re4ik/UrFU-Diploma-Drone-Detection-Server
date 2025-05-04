from src.shared.api.mongo_db import MongoManager, mongo_manager
from datetime import datetime, timedelta


class UpdateUsertLocation:

    def __init__(self, mongo_manager: MongoManager):
        self._mongo_manager = mongo_manager

    def get_location(self, user_id: int) -> tuple[float, float]:
        filter_ = {"userId": user_id}
        with self._mongo_manager.get_collection("user") as collection:
            result = collection.find_one(filter_)
            if result is None:
                raise Exception()
            return (result["latitude"], result["longitude"])

    def update_location(self, user_id: int, latitude: float, longitude: float):
        filter_ = {"userId": user_id}
        update_ = {
            "$set": {
                "latitude": latitude,
                "longitude": longitude,
                "datetime": datetime.now(),
            }
        }
        with self._mongo_manager.get_collection("user") as collection:
            collection.update_one(filter_, update_, upsert=True)

    def time_to_update_location(self, user_id: int) -> bool:

        filter_ = {"userId": user_id}

        with self._mongo_manager.get_collection("user") as collection:
            user_data: dict | None = collection.find_one(filter_)
            if user_data is None:
                return True

            datetime_last_update: datetime = user_data["datetime"]
            if datetime.now() - timedelta(minutes=10) > datetime_last_update:
                return True

        return False


def get_update_user_location():
    return UpdateUsertLocation(mongo_manager)

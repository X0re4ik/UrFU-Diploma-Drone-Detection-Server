

from src.shared.libs.s3 import S3Adapter

import logging


logger = logging.getLogger(__name__)

class ILoadVideo:
    
    def download(self, unique_id: str) -> str:
        """_summary_

        Args:
            unique_id (str): _description_

        Returns:
            str: _description_
        """

class LoadVideoToLocal(ILoadVideo):
    
    def __init__(self, s3_adapter: S3Adapter, bucket: str):
        self._s3_adapter = s3_adapter
        self._bucket = bucket
    
    def download(self, unique_id: str) -> str:
        key = f"/rows/{unique_id}.mp4"
        file_path = self._s3_adapter.download_to_tmp(self._bucket, key)
        logger.info(file_path)
        return file_path
        
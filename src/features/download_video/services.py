from src.shared.libs.s3 import S3Adapter


import os


from src.shared.libs.s3 import S3Adapter

from src.shared.configs import settings


def _s3_create_adapter():
    return S3Adapter(
        settings.s3.host,
        settings.s3.port,
        settings.s3.access_key,
        settings.s3.secret_key,
        use_ssl=settings.s3.use_ssl,
    ).initialize()


class DownloadVideo:

    def __init__(self, s3_adapter: S3Adapter, bucket: str):
        self._s3_adapter = s3_adapter
        self._bucket = bucket

    def download(self, path_to_file: str) -> str:
        name = os.path.basename(path_to_file)
        key = f"/processed/{name}"
        with open(path_to_file, "rb") as file:
            self._s3_adapter.upload_file(self._bucket, key, file.read(), "video/mp4", metadata={
            'Content-Disposition': 'inline'
        })

        return key


def get_download_video():
    return DownloadVideo(_s3_create_adapter(), settings.s3.bucket)

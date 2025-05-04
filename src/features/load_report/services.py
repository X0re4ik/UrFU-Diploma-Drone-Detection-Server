import io
from src.shared.libs.s3 import S3Adapter

import matplotlib.pyplot as plt


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


class LoadReport:

    def __init__(self, s3_adapter: S3Adapter, bucket: str):
        self._s3_adapter = s3_adapter
        self._bucket = bucket

        self._generate_key = lambda name: f"/reports/{name}"

    def save_report(self, figure: plt.Figure, name: str) -> str:
        buffer = io.BytesIO()
        figure.savefig(buffer, format="png", bbox_inches="tight", dpi=150)
        buffer.seek(0)

        self._s3_adapter.upload_file(
            self._bucket, self._generate_key(name), buffer.getvalue()
        )
        return self._generate_key(name)

    def get_report(self, name: str) -> tuple[str, bytes]:
        return self._s3_adapter.download_file_bytes(
            self._bucket, self._generate_key(name)
        )


def get_report():
    return LoadReport(_s3_create_adapter(), settings.s3.bucket)

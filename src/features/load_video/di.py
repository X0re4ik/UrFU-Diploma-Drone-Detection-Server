from .service import ILoadVideo, LoadVideoToLocal

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


class LoadVideoFactory:

    @staticmethod
    def create() -> ILoadVideo:
        return LoadVideoToLocal(_s3_create_adapter(), settings.s3.bucket)

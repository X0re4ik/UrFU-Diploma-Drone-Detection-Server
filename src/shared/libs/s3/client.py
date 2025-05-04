import os
import boto3
from botocore.exceptions import ClientError


from typing_extensions import Self


class S3Adapter:

    def __init__(
        self,
        host: str,
        port: int,
        aws_access_key: str,
        aws_secret_key: str,
        region_name: str = "us-east-1",
        use_ssl: bool = True,
    ):
        self._host = host
        self._port = port

        self._aws_access_key = aws_access_key
        self._aws_secret_key = aws_secret_key

        self._region_name = region_name
        self._use_ssl = use_ssl
        self._http = "https" if self._use_ssl else "http"
        self._endpoint_url = self._http + "://" + self._host + ":" + str(self._port)

    def initialize(self) -> Self:

        self._client = boto3.client(
            "s3",
            aws_access_key_id=self._aws_access_key,
            aws_secret_access_key=self._aws_secret_key,
            region_name=self._region_name,
            endpoint_url=self._endpoint_url,
            verify=False,
            use_ssl=self._use_ssl,
        )

        return self

    def get_bublick_url(self, full_path: str) -> str:
        if not full_path or "/" not in full_path:
            raise ValueError("full_path должен быть в формате 'bucket/key'")
        return f"{self._endpoint_url}/{full_path}"
    
    def get_presigned_url(self, bucket: str, key: str, expires_in: int = 600) -> str:
        """
        Генерирует временную ссылку на объект S3/MinIO.

        :param bucket: Название бакета
        :param key: Ключ (путь к объекту внутри бакета)
        :param expires_in: Время жизни ссылки в секундах (по умолчанию 10 минут)
        :return: Временная URL-ссылка
        """
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    def file_exists(self, bucket: str, key: str) -> bool:
        try:
            self._client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                raise

    def upload_file(
        self,
        bucket: str,
        path: str,
        content: bytes,
        content_type: str = "application/octet-stream",
        *,
        metadata: dict | None = None,
    ) -> None:
        kwargs = {
            "Bucket": bucket, "Key": path, "Body": content, "ContentType": content_type
        }
        if metadata:
            kwargs.update({"Metadata": metadata})
        self._client.put_object(
            **kwargs
        )

    def download_to_tmp(
        self, bucket: str, key: str, tmp_template: str = "/tmp/drones/rows/"
    ) -> str:
        local_path = os.path.join(tmp_template, os.path.basename(key))
        with open(local_path, "wb") as f:
            self._client.download_fileobj(Bucket=bucket, Key=key, Fileobj=f)

        return local_path

    def download_file_bytes(self, bucket: str, key: str) -> tuple[str, bytes]:
        """
        Загружает файл из S3 и возвращает его имя и содержимое в байтах.

        :param bucket: Название бакета
        :param key: Путь (ключ) файла в бакете
        :return: (имя файла, содержимое в байтах)
        """
        from io import BytesIO

        buffer = BytesIO()
        self._client.download_fileobj(Bucket=bucket, Key=key, Fileobj=buffer)
        buffer.seek(0)

        filename = os.path.basename(key)
        return filename, buffer.read()

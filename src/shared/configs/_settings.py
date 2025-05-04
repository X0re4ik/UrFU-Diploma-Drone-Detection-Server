from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class BaseConfig(BaseSettings):
    """_summary_

    Args:
        BaseSettings (_type_): _description_

    Returns:
        _type_: _description_
    """

class APPConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="APP_")


class S3ClientConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="S3_")

    host: str
    port: int

    bucket: str

    access_key: str
    secret_key: str

    use_ssl: bool = Field(default=False)


class MongoDBConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="MONGO_DB_")

    user: str
    password: str
    host: str
    port: int
    name: str

    @property
    def URI(self) -> str:
        return (
            f"mongodb://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/"
            f"{self.name}"
        )


class Settings(BaseConfig):
    db: MongoDBConfig = Field(default_factory=MongoDBConfig)
    s3: S3ClientConfig = Field(default_factory=S3ClientConfig)
    
    app: APPConfig = Field(default_factory=APPConfig)



from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ConfigDict, Field
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные из .env

class BaseConfig(BaseSettings):
    """_summary_

    Args:
        BaseSettings (_type_): _description_

    Returns:
        _type_: _description_
    """
    model_config = SettingsConfigDict(
        extra="allow",
        env_file='.env',
        env_file_encoding='utf-8'
    )

class TelegramBotConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="TELEGRAM_BOT_")

    user_token: str
    service_token: str
    service_chat_id: str


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
    telegram_bot: TelegramBotConfig = Field(default_factory=TelegramBotConfig)
    app: APPConfig = Field(default_factory=APPConfig)



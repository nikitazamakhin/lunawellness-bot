from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    bot_token: str = ""
    admin_id: int = 0

    class Config:
        env_file = Path(__file__).parent.parent / ".env"
        env_file_encoding = "utf-8"


settings = Settings()

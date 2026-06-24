from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    bot_token: str = ""
    admin_id: int = 0

    # Odoo CRM Integration
    odoo_api_url: Optional[str] = None
    odoo_api_token: Optional[str] = None

    class Config:
        env_file = Path(__file__).parent.parent / ".env"
        env_file_encoding = "utf-8"


settings = Settings()

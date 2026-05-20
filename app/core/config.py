from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    
    # Configuration SFTP
    SFTP_HOST: Optional[str] = None
    SFTP_PORT: int = 22
    SFTP_USERNAME: Optional[str] = None
    SFTP_PASSWORD: Optional[str] = None
    SFTP_REMOTE_PATH: str = "/"
    SFTP_REMOTE_PATH_MONTHLY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

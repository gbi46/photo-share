from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pydantic import Field
from src.conf.config_init import InitialSettings

init_settings = InitialSettings()
env_name = init_settings.ENV_APP

base_dir = Path(__file__).resolve().parent
env_file_path = base_dir / f".env.{env_name}"

env_file = str(env_file_path) if env_file_path.exists() else None

class Settings(BaseSettings):
    ENV_APP: str = env_name
    DB_URL: str = Field(..., alias="DATABASE_URL")
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    ALGORITHM: str
    REFRESH_SECRET_KEY: str
    SECRET_KEY: str

    CLD_NAME: str
    CLD_API_KEY: int
    CLD_API_SECRET: str
    MAX_POST_TAGS: int

    model_config = ConfigDict(
        env_file=env_file,                    
        env_file_encoding="utf-8",            
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()


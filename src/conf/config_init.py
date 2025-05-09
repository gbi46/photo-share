from pydantic_settings import BaseSettings

class InitialSettings(BaseSettings):
    ENV_APP: str = "development"

    class Config:
        env_file = ".env.base"

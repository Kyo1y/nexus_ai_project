from pydantic import BaseSettings


class Settings(BaseSettings):
    title: str = ""
    version: str = ""
    env_name: str = ""
    port: int = ""
    gpt_key: str = ""
    gpt_timeout: int = ""
    gpt_call_limit: int = ""
    DATA_URL: str = ""

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    settings = Settings()
    return settings
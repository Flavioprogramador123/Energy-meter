from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Pieng Medidor Master"
    api_prefix: str = "/api"
    database_url: str = "sqlite:///./data/app.db"
    enable_forwarding: bool = True
    forwarder_url: str | None = None
    scheduler_timezone: str = "UTC"

    class Config:
        env_file = ".env"


settings = Settings()


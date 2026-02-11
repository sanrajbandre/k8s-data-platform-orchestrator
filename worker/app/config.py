from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    celery_broker_url: str = "redis://127.0.0.1:6379/0"
    celery_result_backend: str = "redis://127.0.0.1:6379/1"
    db_url: str = "mysql+pymysql://root:root@127.0.0.1:3306/orchestrator?charset=utf8mb4"
    prometheus_base_url: str = "http://127.0.0.1:9090"

    webhook_url: str = ""
    slack_webhook_url: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = "noreply@example.local"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

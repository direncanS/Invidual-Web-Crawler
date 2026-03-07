from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str

    jwt_secret: str
    jwt_expires_seconds: int = 86400

    smtp_host: str = "mailhog"
    smtp_port: int = 1025
    smtp_from: str = "no-reply@local.test"
    reset_token_ttl_seconds: int = 60

    storage_root: str = "/data"

    max_pages_per_job: int = 200
    request_timeout_seconds: int = 10
    rate_limit_seconds: float = 0.5

    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"

    cors_origins: str = ""

    class Config:
        env_prefix = ""
        case_sensitive = False

settings = Settings()
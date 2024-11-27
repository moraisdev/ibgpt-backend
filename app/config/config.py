from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=1, env="REFRESH_TOKEN_EXPIRE_DAYS")
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    OPENAI_API_KEY: str = Field(..., env="openai_api_key")
    KAFKA_BROKER: str = Field(..., env="kafka_broker")
    KAFKA_TOPIC_RESPONSES: str = Field(..., env="kafka_topic_responses")
    KAFKA_TOPIC_PROSPECTION: str = Field(..., env="kafka_topic_prospection")
    POSTGRES_USER: str = Field(..., env="postgres_user")
    POSTGRES_PASSWORD: str = Field(..., env="postgres_password")
    POSTGRES_DB: str = Field(..., env="postgres_db")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

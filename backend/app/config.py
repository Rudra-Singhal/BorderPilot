from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://borderpilot:borderpilot@localhost:5544/borderpilot"
    aws_region: str = "eu-north-1"
    bedrock_model_id: str = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"


settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str
    opensearch_url: str
    aws_endpoint_url: str
    aws_region: str = "us-east-1"
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"
    s3_bucket: str = "recallai-files"
    anthropic_api_key: str = "test"
    langchain_tracing_v2: bool = True
    langchain_api_key: str = "test"

settings = Settings()
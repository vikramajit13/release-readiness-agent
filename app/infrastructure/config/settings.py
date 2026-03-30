from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "RELEASE-READINESS-AGENT"
    DATABASE_URL: str
    EMBEDDING_MODEL: str
    ENCODER_MODEL: str
    OLLAMA_HOST: str
    BUCKET_NAME:str
    REGION_NAME:str
    AWS_ACCESS_KEY: str
    AWS_ACCESS_KEY_ID:str
    AWS_SECRET_ACCESS_KEY: str
    AWS_SESSION_TOKEN: str
    ENDPOINT_URL: str
    SQS_QUEUE_URL: str
    AWS_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_SESSION_TOKEN: str
    SQS_ENDPOINT_URL: str

    # This tells Pydantic to look for a .env file
    model_config = SettingsConfigDict(env_file=find_dotenv())


# Instantiate once to be used across the app
settings = Settings()

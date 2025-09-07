from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    """
    Manages application configuration using environment variables.

    Pydantic's BaseSettings provides automatic validation and type-hinting for
    environment variables. If a required variable is missing, the app will
    fail to start with a clear error message.
    """
    MISTRAL_API_KEY: str

settings = Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "sqlite+aiosqlite:///./db.sqlite3"
    WHISPER_SERVER_URL: str = "http://localhost:8001/transcribe"
    RASA_SERVER_URL: str = "http://localhost:5005/webhooks/rest/webhook"

    model_config = SettingsConfigDict(env_file=".env", extra='ignore', env_file_encoding='utf-8')

settings = Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    WHISPER_SERVER_URL: str
    RASA_SERVER_URL: str
    GEMINI_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()

#if __name__ == "__main__":
#    print(settings.dict())
    # This will print the settings loaded from the .env file
    # Make sure to have a .env file with the required variables in the same directory
    # Example content of .env:
    # SQLALCHEMY_DATABASE_URL=sqlite:///./test.db
    # WHISPER_SERVER_URL=http://localhost:5000
    # RASA_SERVER_URL=http://localhost:5005
    # GEMINI_API_KEY=your_api_key_here
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "SafeSound"
    DEBUG: bool = True
    HOST: str = "localhost"
    PORT: int = 8000

    # Whisper settings
    DEFAULT_WHISPER_MODEL: str = "turbo"
    AVAILABLE_MODELS: List[str] = ["small", "medium", "turbo"]

    # File upload settings
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: List[str] = [
        ".mp3",
        ".wav",
        ".m4a",
        ".flac",
        ".ogg",
        ".opus",
    ]
    UPLOAD_DIR: str = "uploads"

    # Audio processing settings
    CHUNK_DURATION: int = 5  # seconds for real-time processing
    SAMPLE_RATE: int = 16000

    class Config:
        env_file = ".env"


# Create uploads directory if it doesn't exist
if not os.path.exists("uploads"):
    os.makedirs("uploads")

settings = Settings()

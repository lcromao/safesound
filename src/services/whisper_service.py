import whisper
import torch
import tempfile
import os
import time
from typing import Optional, Tuple
from pydub import AudioSegment
from src.core.config import settings
from src.schemas.transcribe_schemas import WhisperModel, TranscriptionAction
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhisperService:
    def __init__(self):
        self.models = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

    def load_model(self, model_name: str) -> whisper.Whisper:
        """Load and cache Whisper model"""
        if model_name not in self.models:
            logger.info(f"Loading Whisper model: {model_name}")
            self.models[model_name] = whisper.load_model(
                model_name, device=self.device
            )
            logger.info(f"Model {model_name} loaded successfully")
        return self.models[model_name]

    def preprocess_audio(self, audio_path: str) -> str:
        """Convert audio to format compatible with Whisper"""
        try:
            # Load audio file
            audio = AudioSegment.from_file(audio_path)

            # Convert to WAV format with correct sample rate
            audio = audio.set_frame_rate(settings.SAMPLE_RATE)
            audio = audio.set_channels(1)  # Convert to mono

            # Create temporary file
            with tempfile.NamedTemporaryFile(
                suffix=".wav", delete=False
            ) as temp_file:
                temp_path = temp_file.name
                audio.export(temp_path, format="wav")

            return temp_path

        except Exception as e:
            logger.error(f"Error preprocessing audio: {str(e)}")
            raise

    def transcribe_audio(
        self,
        audio_path: str,
        model: WhisperModel = WhisperModel.TURBO,
        action: TranscriptionAction = TranscriptionAction.TRANSCRIBE,
        language: Optional[str] = None,
    ) -> Tuple[str, str, float]:
        """
        Transcribe audio file using Whisper

        Returns:
            Tuple of (transcribed_text, detected_language, processing_time)
        """
        start_time = time.time()
        temp_path = None

        try:
            # Load the specified model
            whisper_model = self.load_model(model.value)

            # Preprocess audio
            temp_path = self.preprocess_audio(audio_path)

            # Prepare options
            options = {}
            if action == TranscriptionAction.TRANSLATE:
                options["task"] = "translate"
            else:
                options["task"] = "transcribe"

            if language:
                options["language"] = language

            # Perform transcription
            logger.info(f"Starting {action.value} with model {model.value}")
            result = whisper_model.transcribe(temp_path, **options)

            processing_time = time.time() - start_time

            return (
                result["text"].strip(),
                result.get("language", "unknown"),
                processing_time,
            )

        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            raise
        finally:
            # Clean up temporary file
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)

    def transcribe_audio_chunk(
        self,
        audio_data: bytes,
        model: WhisperModel = WhisperModel.TURBO,
        action: TranscriptionAction = TranscriptionAction.TRANSCRIBE,
    ) -> str:
        """
        Transcribe audio chunk for real-time processing
        """
        temp_path = None

        try:
            # Save audio chunk to temporary file
            with tempfile.NamedTemporaryFile(
                suffix=".wav", delete=False
            ) as temp_file:
                temp_path = temp_file.name
                temp_file.write(audio_data)

            # Load model
            whisper_model = self.load_model(model.value)

            # Prepare options
            options = {"task": action.value}

            # Transcribe chunk
            result = whisper_model.transcribe(temp_path, **options)

            return result["text"].strip()

        except Exception as e:
            logger.error(f"Error transcribing audio chunk: {str(e)}")
            return ""
        finally:
            # Clean up
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)


# Global service instance
whisper_service = WhisperService()

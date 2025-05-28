from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum

class WhisperModel(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    TURBO = "turbo"

class TranscriptionAction(str, Enum):
    TRANSCRIBE = "transcribe"
    TRANSLATE = "translate"

class TranscriptionRequest(BaseModel):
    model: WhisperModel = WhisperModel.TURBO
    action: TranscriptionAction = TranscriptionAction.TRANSCRIBE
    language: Optional[str] = None

class TranscriptionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    success: bool
    text: str
    language: Optional[str] = None
    processing_time: float
    model_used: str
    action_performed: str

class TranscriptionProgress(BaseModel):
    progress: int = Field(..., ge=0, le=100)
    status: str
    message: Optional[str] = None

class AudioStreamData(BaseModel):
    audio_data: bytes
    model: WhisperModel = WhisperModel.TURBO
    action: TranscriptionAction = TranscriptionAction.TRANSCRIBE
    chunk_id: int
    is_final: bool = False

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[str] = None

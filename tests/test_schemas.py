import pytest
from pydantic import ValidationError
from src.schemas.transcribe_schemas import (
    WhisperModel, TranscriptionAction, TranscriptionRequest,
    TranscriptionResponse, TranscriptionProgress, AudioStreamData,
    ErrorResponse
)

class TestSchemas:
    def test_whisper_model_enum(self):
        """Test WhisperModel enum values"""
        assert WhisperModel.SMALL.value == "small"
        assert WhisperModel.MEDIUM.value == "medium"
        assert WhisperModel.TURBO.value == "turbo"
    
    def test_transcription_action_enum(self):
        """Test TranscriptionAction enum values"""
        assert TranscriptionAction.TRANSCRIBE.value == "transcribe"
        assert TranscriptionAction.TRANSLATE.value == "translate"
    
    def test_transcription_request_defaults(self):
        """Test TranscriptionRequest with default values"""
        request = TranscriptionRequest()
        assert request.model == WhisperModel.TURBO
        assert request.action == TranscriptionAction.TRANSCRIBE
        assert request.language is None
    
    def test_transcription_request_custom_values(self):
        """Test TranscriptionRequest with custom values"""
        request = TranscriptionRequest(
            model=WhisperModel.SMALL,
            action=TranscriptionAction.TRANSLATE,
            language="pt"
        )
        assert request.model == WhisperModel.SMALL
        assert request.action == TranscriptionAction.TRANSLATE
        assert request.language == "pt"
    
    def test_transcription_response_valid(self):
        """Test valid TranscriptionResponse"""
        response = TranscriptionResponse(
            success=True,
            text="Hello world",
            language="en",
            processing_time=1.5,
            model_used="turbo",
            action_performed="transcribe"
        )
        assert response.success is True
        assert response.text == "Hello world"
        assert response.language == "en"
        assert response.processing_time == 1.5
        assert response.model_used == "turbo"
        assert response.action_performed == "transcribe"
    
    def test_transcription_progress_valid_range(self):
        """Test TranscriptionProgress with valid progress values"""
        progress = TranscriptionProgress(progress=50, status="processing")
        assert progress.progress == 50
        assert progress.status == "processing"
        assert progress.message is None
    
    def test_transcription_progress_invalid_range(self):
        """Test TranscriptionProgress with invalid progress values"""
        with pytest.raises(ValidationError):
            TranscriptionProgress(progress=-1, status="processing")
        
        with pytest.raises(ValidationError):
            TranscriptionProgress(progress=101, status="processing")
    
    def test_audio_stream_data_defaults(self):
        """Test AudioStreamData with default values"""
        data = AudioStreamData(
            audio_data=b"fake audio",
            chunk_id=1
        )
        assert data.audio_data == b"fake audio"
        assert data.model == WhisperModel.TURBO
        assert data.action == TranscriptionAction.TRANSCRIBE
        assert data.chunk_id == 1
        assert data.is_final is False
    
    def test_error_response_defaults(self):
        """Test ErrorResponse with default values"""
        error = ErrorResponse(error="Something went wrong")
        assert error.success is False
        assert error.error == "Something went wrong"
        assert error.details is None
    
    def test_error_response_with_details(self):
        """Test ErrorResponse with details"""
        error = ErrorResponse(
            error="Validation failed",
            details="File size too large"
        )
        assert error.success is False
        assert error.error == "Validation failed"
        assert error.details == "File size too large"

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from src.services.whisper_service import WhisperService
from src.schemas.transcribe_schemas import WhisperModel, TranscriptionAction

class TestWhisperService:
    @pytest.fixture
    def whisper_service(self):
        return WhisperService()
    
    @patch('src.services.whisper_service.whisper.load_model')
    def test_load_model(self, mock_load_model, whisper_service):
        """Test model loading"""
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        
        model = whisper_service.load_model("small")
        
        assert model == mock_model
        mock_load_model.assert_called_once_with("small", device=whisper_service.device)
        
        # Test caching
        model2 = whisper_service.load_model("small")
        assert model2 == mock_model
        # Should not call load_model again due to caching
        mock_load_model.assert_called_once()
    
    def test_preprocess_audio_invalid_file(self, whisper_service):
        """Test preprocessing with invalid audio file"""
        with pytest.raises(Exception):
            whisper_service.preprocess_audio("nonexistent_file.wav")
    
    @patch('src.services.whisper_service.AudioSegment.from_file')
    def test_preprocess_audio_success(self, mock_audio_segment, whisper_service):
        """Test successful audio preprocessing"""
        # Mock audio segment
        mock_audio = Mock()
        mock_audio.set_frame_rate.return_value = mock_audio
        mock_audio.set_channels.return_value = mock_audio
        mock_audio_segment.from_file.return_value = mock_audio
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_file.write(b"fake audio content")
            temp_path = temp_file.name
        
        try:
            result_path = whisper_service.preprocess_audio(temp_path)
            assert result_path.endswith(".wav")
            assert os.path.exists(result_path)
            
            # Cleanup
            os.unlink(result_path)
        finally:
            os.unlink(temp_path)
    
    @patch('src.services.whisper_service.WhisperService.load_model')
    @patch('src.services.whisper_service.WhisperService.preprocess_audio')
    def test_transcribe_audio(self, mock_preprocess, mock_load_model, whisper_service):
        """Test audio transcription"""
        # Setup mocks
        mock_model = Mock()
        mock_model.transcribe.return_value = {
            "text": "Hello world",
            "language": "en"
        }
        mock_load_model.return_value = mock_model
        mock_preprocess.return_value = "processed_audio.wav"
        
        with patch('os.path.exists', return_value=True), \
             patch('os.unlink'):
            
            text, language, time_taken = whisper_service.transcribe_audio(
                "test.mp3",
                WhisperModel.SMALL,
                TranscriptionAction.TRANSCRIBE
            )
            
            assert text == "Hello world"
            assert language == "en"
            assert isinstance(time_taken, float)
            assert time_taken >= 0
            
            mock_load_model.assert_called_once_with("small")
            mock_preprocess.assert_called_once_with("test.mp3")
            mock_model.transcribe.assert_called_once()
    
    @patch('src.services.whisper_service.WhisperService.load_model')
    def test_transcribe_audio_chunk(self, mock_load_model, whisper_service):
        """Test audio chunk transcription"""
        # Setup mock
        mock_model = Mock()
        mock_model.transcribe.return_value = {"text": "Chunk text"}
        mock_load_model.return_value = mock_model
        
        with patch('tempfile.NamedTemporaryFile') as mock_temp, \
             patch('os.path.exists', return_value=True), \
             patch('os.unlink'):
            
            # Mock temporary file
            mock_file = Mock()
            mock_file.name = "temp_chunk.wav"
            mock_temp.return_value.__enter__.return_value = mock_file
            
            result = whisper_service.transcribe_audio_chunk(
                b"fake audio data",
                WhisperModel.TURBO,
                TranscriptionAction.TRANSCRIBE
            )
            
            assert result == "Chunk text"
            mock_load_model.assert_called_once_with("turbo")
            mock_model.transcribe.assert_called_once()

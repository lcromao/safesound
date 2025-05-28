#!/usr/bin/env python3
"""
SafeSound Demo Script
Test the Whisper functionality with a simple audio file
"""

import os
import sys
import tempfile
import time
from pydub import AudioSegment
from pydub.generators import Sine
from src.services.whisper_service import whisper_service
from src.schemas.transcribe_schemas import WhisperModel, TranscriptionAction

def create_test_audio():
    """Create a simple test audio file"""
    print("Creating test audio file...")
    
    # Generate a simple sine wave audio (440Hz for 3 seconds)
    duration = 3000  # 3 seconds in milliseconds
    sample_rate = 16000
    
    sine_wave = Sine(440).to_audio_segment(duration=duration)
    sine_wave = sine_wave.set_frame_rate(sample_rate)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_path = temp_file.name
        sine_wave.export(temp_path, format="wav")
        
    print(f"Test audio created: {temp_path}")
    return temp_path

def test_transcription(audio_path):
    """Test audio transcription"""
    print("\nTesting audio transcription...")
    print(f"Audio file: {audio_path}")
    
    try:
        # Test transcription
        start_time = time.time()
        text, language, processing_time = whisper_service.transcribe_audio(
            audio_path,
            WhisperModel.SMALL,  # Using small model for faster testing
            TranscriptionAction.TRANSCRIBE
        )
        
        print(f"\nTranscription Results:")
        print(f"  Text: '{text}'")
        print(f"  Language: {language}")
        print(f"  Processing Time: {processing_time:.2f} seconds")
        print(f"  Total Time: {time.time() - start_time:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return False

def main():
    """Main demo function"""
    print("SafeSound Demo - Testing Whisper Integration")
    print("=" * 50)
    
    # Check if we can import whisper
    try:
        import whisper
        print("✓ OpenAI Whisper imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Whisper: {e}")
        return 1
    
    # Check available models
    print(f"✓ Available models: {[model.value for model in WhisperModel]}")
    
    # Create test audio
    audio_path = None
    try:
        audio_path = create_test_audio()
        
        # Test transcription
        success = test_transcription(audio_path)
        
        if success:
            print("\n✓ Demo completed successfully!")
            print("\nYour SafeSound application is ready to use!")
            print("Access it at: http://localhost:8000")
            return 0
        else:
            print("\n✗ Demo failed during transcription")
            return 1
            
    except Exception as e:
        print(f"\n✗ Demo failed: {str(e)}")
        return 1
        
    finally:
        # Cleanup
        if audio_path and os.path.exists(audio_path):
            os.unlink(audio_path)
            print(f"Cleaned up test audio: {audio_path}")

if __name__ == "__main__":
    sys.exit(main())

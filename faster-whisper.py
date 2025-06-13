import pyaudio
import numpy as np

# Reduced chunk size to prevent overflow
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

from faster_whisper import WhisperModel

model_size = "small"

# TODO: Inserir turn detection


def send_audio():
    p = pyaudio.PyAudio()
    stream = None

    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
        )

        model = WhisperModel(model_size, device="cpu", compute_type="int8")

        # Buffer to accumulate audio data
        audio_buffer = []
        buffer_duration = 2  # seconds
        buffer_size = RATE * buffer_duration

        print("Listening... Press Ctrl+C to stop")

        while True:
            try:
                # Read audio data with error handling
                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                audio_buffer.extend(np.frombuffer(data, dtype=np.int16))

                # Process when we have enough audio data
                if len(audio_buffer) >= buffer_size:
                    # Convert to float32 and normalize
                    numpy_data = (
                        np.array(audio_buffer, dtype=np.float32) / 32768.0
                    )

                    # Transcribe the audio
                    segments, info = model.transcribe(
                        numpy_data, beam_size=5, language="pt"
                    )

                    for segment in segments:
                        print(
                            "[%.2fs -> %.2fs] %s"
                            % (segment.start, segment.end, segment.text)
                        )

                    # Clear the buffer
                    audio_buffer = []

            except OSError as e:
                if e.errno == -9981:  # Input overflow
                    print("Warning: Audio input overflow, skipping frame...")
                    continue
                else:
                    raise e

    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Safely close the stream and terminate
        if stream is not None:
            try:
                if stream.is_active():
                    stream.stop_stream()
                stream.close()
            except:
                pass  # Ignore errors when closing
        p.terminate()


if __name__ == "__main__":
    send_audio()

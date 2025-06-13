# Importa as bibliotecas necessárias
import whisper  # Importa a biblioteca openai-whisper
import pyaudio
import wave
import os

DEVICE = "cpu"  # Define o dispositivo como CPU
FP16 = False  # fp16=False para CPU
LANGUAGE = "pt"  # Define o idioma como português
CHUNK_LENGTH = 1  # Duração do chunk em segundos


def transcribe_chunk(model, file_path):
    """
    Transcreve um trecho de áudio usando o modelo openai-whisper.

    Args:
        model: A instância do modelo Whisper.
        file_path: Caminho para o arquivo de áudio a ser transcrito.

    Returns:
        str: A transcrição do áudio.
    """
    # A função transcribe do openai-whisper retorna um dicionário
    result = model.transcribe(file_path, fp16=FP16, language=LANGUAGE)
    return result["text"]


def record_chunk(p, stream, file_path, chunk_length=CHUNK_LENGTH):
    """
    Grava um trecho de áudio e salva em um arquivo .wav.

    Args:
        p (pyaudio.PyAudio): Instância do PyAudio.
        stream: Stream de áudio aberto.
        file_path (str): Caminho para salvar o arquivo.
        chunk_length (int): Duração da gravação em segundos.
    """
    frames = []
    # Lê os dados do stream de áudio
    for _ in range(0, int(16000 / 1024 * chunk_length)):
        data = stream.read(1024, exception_on_overflow=False)
        frames.append(data)

    # Salva os dados gravados em um arquivo .wav
    wf = wave.open(file_path, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b"".join(frames))
    wf.close()


def main():
    # Modelos disponíveis: tiny, base, small, medium, large
    # O modelo "base" é um bom ponto de partida para testes em CPU.
    model_name = "small"

    print(f"Carregando o modelo Whisper '{model_name}'...")
    # Carrega o modelo usando a função whisper.load_model
    model = whisper.load_model(model_name, device=DEVICE)
    print("Modelo carregado com sucesso!")

    p = pyaudio.PyAudio()
    stream = None  # Inicializa o stream como None

    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024,
            input_device_index=None,
        )

        accumulated_transcription = ""
        print("\n--- Pressione Ctrl+C para parar a transcrição ---")

        while True:
            file_path = "temp_chunk.wav"
            record_chunk(
                p, stream, file_path, chunk_length=5
            )  # Aumentei para 5s

            # Transcreve o trecho gravado
            transcription = transcribe_chunk(model, file_path)

            print(transcription)

            os.remove(file_path)  # Remove o arquivo temporário
            accumulated_transcription += str(transcription) + " "

    except KeyboardInterrupt:
        print("\n--- Transcrição interrompida pelo usuário ---")
        print("\nTranscrição Final Completa:")
        print(accumulated_transcription.strip())
    except Exception as e:
        print(f"\nOcorreu um erro: {e}")
    finally:
        # Garante que o stream e o pyaudio sejam devidamente fechados
        if stream and stream.is_active():
            stream.stop_stream()
        if stream:
            stream.close()
        if p:
            p.terminate()


if __name__ == "__main__":
    main()

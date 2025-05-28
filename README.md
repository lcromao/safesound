# SafeSound - Audio Transcription Application

SafeSound is a complete web application for audio transcription using the **OpenAI Whisper** model. The application allows transcription of audio files uploaded by users and real-time transcription from microphone input.

## 🚀 Features

- **Upload Transcription**: Support for MP3, WAV, M4A, FLAC, OGG files
- **Real-time Transcription**: Capture and transcription via microphone
- **Multiple Whisper Models**: Small, Medium, Turbo
- **Translation**: Transcribe and translate to English
- **Modern Interface**: Light/dark theme, drag & drop
- **Visual Progress**: Progress bar during processing
- **Export**: Copy and download transcriptions

## 🛠️ Technologies

- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, CSS3, JavaScript ES6
- **AI**: OpenAI Whisper
- **Containerization**: Docker, Docker Compose
- **Python Manager**: Conda

## 📋 Prerequisites

### Option 1: Docker (Recommended)
- Docker
- Docker Compose

### Option 2: Local Development
- Python 3.9+
- Conda
- FFmpeg
- Git

## 🚀 Installation and Setup

### Using Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd safesound
```

2. **Run with Docker Compose**
```bash
docker-compose up --build
```

3. **Access the application**
```
http://localhost:8000
```

### Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd safesound
```

2. **Install FFmpeg**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

3. **Create Conda environment**
```bash
conda env create -f environment.yml
conda activate safesound
```

4. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

5. **Run the application**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

6. **Access the application**
```
http://localhost:8000
```

## 📁 Project Structure

```
safesound/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── environment.yml         # Conda environment
├── Dockerfile             # Docker image
├── docker-compose.yml     # Container orchestration
├── README.md              # Documentation
├── src/
│   ├── core/              # Application configuration
│   │   ├── __init__.py
│   │   └── config.py
│   ├── routes/            # API endpoints
│   │   ├── __init__.py
│   │   └── transcribe.py
│   ├── schemas/           # Pydantic models
│   │   ├── __init__.py
│   │   └── transcribe_schemas.py
│   ├── services/          # Business logic
│   │   ├── __init__.py
│   │   └── whisper_service.py
│   ├── templates/         # HTML templates
│   │   └── index.html
│   └── static/            # Static files
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── script.js
│       └── images/
├── tests/                 # Unit tests
└── uploads/               # Upload directory (created automatically)
```

## 🎯 How to Use

### 1. Upload Transcription

1. Select the Whisper model (Small, Medium, Turbo)
2. Choose the action (Transcribe or Translate)
3. Drag an audio file or click "Choose File"
4. Click "Transcribe File"
5. Wait for processing and view the result

### 2. Real-time Transcription

1. Configure the desired model and action
2. Click the microphone button
3. Allow microphone access when prompted
4. Speak near the microphone
5. Click again to stop recording
6. View real-time transcription

### 3. Manage Results

- **Copy**: Copies text to clipboard
- **Download**: Saves transcription as .txt file
- **Clear**: Removes text from interface

### 4. Dark Theme

Use the toggle in the top right corner to switch between light and dark theme. Preference is saved automatically.

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root to customize settings:

```env
# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Whisper
DEFAULT_WHISPER_MODEL=turbo

# Upload
MAX_FILE_SIZE=104857600  # 100MB in bytes
UPLOAD_DIR=uploads

# Audio
CHUNK_DURATION=5
SAMPLE_RATE=16000
```

### Available Whisper Models

- **Small**: Fast, lower accuracy (~39 MB)
- **Medium**: Balanced speed and accuracy (~769 MB)
- **Turbo**: Optimized, good speed and accuracy (~809 MB)

## 📊 API Endpoints

### File Upload
```http
POST /api/upload_audio
Content-Type: multipart/form-data

Parameters:
- file: audio file
- model: whisper model (small|medium|turbo)
- action: action (transcribe|translate)
- language: optional language
```

### Real-time Transcription
```http
WebSocket /api/transcribe_stream

Messages:
- Initial configuration (JSON)
- Audio chunks (binary)
- Transcription responses (JSON)
```

### Available Models
```http
GET /api/models

Response:
{
  "models": ["small", "medium", "turbo"],
  "default": "turbo"
}
```

### Health Check
```http
GET /api/health

Response:
{
  "status": "healthy",
  "service": "SafeSound API"
}
```

## 🧪 Testing

Run unit tests:

```bash
# With pytest
conda activate safesound
pytest tests/

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## 🐛 Troubleshooting

### Microphone Permission Error
- Check if browser has permission to access microphone
- Use HTTPS in production (required for microphone)

### File Upload Error
- Check if file is in supported format
- Confirm size doesn't exceed 100MB
- Make sure there's sufficient disk space

### Whisper Model Error
- Wait for model download on first run
- Check internet connection for model downloads
- Confirm sufficient disk space

### Slow Performance
- Use GPU if available (CUDA)
- Consider using smaller models (small) for faster speed
- Check system resources (RAM, CPU)

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech-to-text model
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [PyTorch](https://pytorch.org/) - Machine learning framework

## 📞 Support

For support, open an issue on GitHub or contact via email.

---

Developed with ❤️ to simplify audio transcription

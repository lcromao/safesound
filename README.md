# SafeSound - Aplicativo de Transcrição de Áudio

SafeSound é uma aplicação web completa para transcrição de áudio utilizando o modelo **OpenAI Whisper**. O aplicativo permite transcrição de arquivos de áudio enviados pelo usuário e transcrição em tempo real a partir do microfone.

## 🚀 Funcionalidades

- **Transcrição por Upload**: Suporte a arquivos MP3, WAV, M4A, FLAC, OGG
- **Transcrição em Tempo Real**: Captura e transcrição via microfone
- **Múltiplos Modelos Whisper**: Small, Medium, Turbo
- **Tradução**: Transcrever e traduzir para inglês
- **Interface Moderna**: Tema claro/escuro, drag & drop
- **Progresso Visual**: Barra de progresso durante processamento
- **Exportação**: Copiar e baixar transcrições

## 🛠️ Tecnologias

- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, CSS3, JavaScript ES6
- **IA**: OpenAI Whisper
- **Containerização**: Docker, Docker Compose
- **Gerenciador Python**: Conda

## 📋 Pré-requisitos

### Opção 1: Docker (Recomendado)
- Docker
- Docker Compose

### Opção 2: Desenvolvimento Local
- Python 3.8-3.11 (recomendado 3.9)
- Conda
- FFmpeg
- Git

## 🚀 Instalação e Execução

### Usando Docker (Recomendado)

1. **Clone o repositório**
```bash
git clone <repository-url>
cd safesound
```

2. **Execute com Docker Compose**
```bash
docker-compose up --build
```

3. **Acesse a aplicação**
```
http://localhost:8000
```

### Desenvolvimento Local

1. **Clone o repositório**
```bash
git clone <repository-url>
cd safesound
```

2. **Instale FFmpeg**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# Baixe de https://ffmpeg.org/download.html
```

3. **Crie o ambiente Conda**
```bash
conda env create -f environment.yml
conda activate safesound
```

4. **Instale dependências Python**
```bash
pip install -r requirements.txt
```

5. **Execute a aplicação**
```bash
uvicorn main:app --host localhost --port 8000 --reload
```

6. **Acesse a aplicação**
```
http://localhost:8000
```

## 📁 Estrutura do Projeto

```
safesound/
├── main.py                 # Ponto de entrada da aplicação
├── requirements.txt        # Dependências Python
├── environment.yml         # Ambiente Conda
├── Dockerfile             # Imagem Docker
├── docker-compose.yml     # Orquestração de containers
├── README.md              # Documentação
├── src/
│   ├── core/              # Configurações da aplicação
│   │   ├── __init__.py
│   │   └── config.py
│   ├── routes/            # Endpoints da API
│   │   ├── __init__.py
│   │   └── transcribe.py
│   ├── schemas/           # Modelos Pydantic
│   │   ├── __init__.py
│   │   └── transcribe_schemas.py
│   ├── services/          # Lógica de negócio
│   │   ├── __init__.py
│   │   └── whisper_service.py
│   ├── templates/         # Templates HTML
│   │   └── index.html
│   └── static/            # Arquivos estáticos
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── script.js
│       └── images/
├── tests/                 # Testes unitários
└── uploads/               # Diretório de uploads (criado automaticamente)
```

## 🎯 Como Usar

### 1. Transcrição por Upload

1. Selecione o modelo Whisper (Small, Medium, Turbo)
2. Escolha a ação (Transcrever ou Traduzir)
3. Arraste um arquivo de áudio ou clique em "Escolher Arquivo"
4. Clique em "Transcrever Arquivo"
5. Aguarde o processamento e visualize o resultado

### 2. Transcrição em Tempo Real

1. Configure o modelo e ação desejados
2. Clique no botão do microfone
3. Permita o acesso ao microfone quando solicitado
4. Fale próximo ao microfone
5. Clique novamente para parar a gravação
6. Visualize a transcrição em tempo real

### 3. Gerenciar Resultados

- **Copiar**: Copia o texto para área de transferência
- **Baixar**: Salva a transcrição como arquivo .txt
- **Limpar**: Remove o texto da interface

### 4. Tema Escuro

Use o toggle no canto superior direito para alternar entre tema claro e escuro. A preferência é salva automaticamente.

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto para personalizar configurações:

```env
# Aplicação
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Whisper
DEFAULT_WHISPER_MODEL=turbo

# Upload
MAX_FILE_SIZE=104857600  # 100MB em bytes
UPLOAD_DIR=uploads

# Áudio
CHUNK_DURATION=5
SAMPLE_RATE=16000
```

### Modelos Whisper Disponíveis

- **Small**: Rápido, menor precisão (~39 MB)
- **Medium**: Balanceado entre velocidade e precisão (~769 MB)
- **Turbo**: Otimizado, boa velocidade e precisão (~809 MB)

## 📊 API Endpoints

### Upload de Arquivo
```http
POST /api/upload_audio
Content-Type: multipart/form-data

Parameters:
- file: arquivo de áudio
- model: modelo whisper (small|medium|turbo)
- action: ação (transcribe|translate)
- language: idioma opcional
```

### Transcrição em Tempo Real
```http
WebSocket /api/transcribe_stream

Mensagens:
- Configuração inicial (JSON)
- Chunks de áudio (binary)
- Respostas de transcrição (JSON)
```

### Modelos Disponíveis
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

## 🧪 Testes

Execute os testes unitários:

```bash
# Com pytest
conda activate safesound
pytest tests/

# Com coverage
pytest tests/ --cov=src --cov-report=html
```

## 🐛 Solução de Problemas

### Erro de Permissão do Microfone
- Verifique se o navegador tem permissão para acessar o microfone
- Use HTTPS em produção (obrigatório para microfone)

### Erro de Upload de Arquivo
- Verifique se o arquivo está em formato suportado
- Confirme se o tamanho não excede 100MB
- Certifique-se de que há espaço em disco suficiente

### Erro de Modelo Whisper
- Aguarde o download do modelo na primeira execução
- Verifique conexão com internet para download dos modelos
- Confirme se há espaço em disco suficiente

### Performance Lenta
- Use GPU se disponível (CUDA)
- Considere usar modelos menores (small) para maior velocidade
- Verifique recursos do sistema (RAM, CPU)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🙏 Agradecimentos

- [OpenAI Whisper](https://github.com/openai/whisper) - Modelo de speech-to-text
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [PyTorch](https://pytorch.org/) - Framework de machine learning

## 📞 Suporte

Para suporte, abra uma issue no GitHub ou entre em contato através do email.

---

Desenvolvido com ❤️ para facilitar a transcrição de áudio

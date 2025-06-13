#!/bin/bash
# SafeSound Setup Script
# This script helps set up the SafeSound application

set -e

echo "🎙️  SafeSound Setup Script"
echo "=========================="

# Check if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✓ Detected macOS"
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew not found. Please install Homebrew first:"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    # Install ffmpeg if not present
    if ! command -v ffmpeg &> /dev/null; then
        echo "📦 Installing ffmpeg..."
        brew install ffmpeg
    else
        echo "✓ ffmpeg is already installed"
    fi
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "✓ Detected Linux"
    
    # Update package list
    echo "📦 Updating package list..."
    sudo apt update
    
    # Install ffmpeg
    if ! command -v ffmpeg &> /dev/null; then
        echo "📦 Installing ffmpeg..."
        sudo apt install -y ffmpeg
    else
        echo "✓ ffmpeg is already installed"
    fi
    
else
    echo "❌ Unsupported operating system. Please install ffmpeg manually."
    exit 1
fi

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Miniconda or Anaconda:"
    echo "   https://docs.conda.io/en/latest/miniconda.html"
    exit 1
else
    echo "✓ Conda is available"
fi

# Create conda environment
echo "🐍 Creating conda environment..."
if conda env list | grep -q "safesound"; then
    echo "✓ SafeSound environment already exists"
    echo "⚠️  To recreate it, run: conda env remove -n safesound"
else
    conda env create -f environment.yml
    echo "✓ SafeSound environment created"
fi

# Activate environment and install dependencies
echo "📦 Installing Python dependencies..."
eval "$(conda shell.bash hook)"
conda activate safesound
pip install -r requirements.txt

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "To start using SafeSound:"
echo "1. Activate the environment: conda activate safesound"
echo "2. Start the server: conda run -n safesound uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
echo "   OR (after activating): uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
echo "3. Open your browser: http://localhost:8000"
echo ""
echo "Or use Docker:"
echo "1. Build and run: docker-compose up --build"
echo "2. Open your browser: http://localhost:8000"

#!/bin/bash

echo "🚀 Setting up UK Job Hunt - Software Engineering Jobs Scraper"
echo "============================================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

echo "✓ pip3 found"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Python dependencies installed successfully"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama is not installed."
    echo "Please install Ollama from: https://ollama.ai/"
    echo "After installation, run: ollama pull llama2"
else
    echo "✓ Ollama found"
    
    # Check if the model is available
    if ollama list | grep -q "llama3.1"; then
        echo "✓ llama3.1 model is available"
    else
        echo "📥 Downloading llama3.1 model..."
        ollama pull llama3.1
        if [ $? -eq 0 ]; then
            echo "✓ llama3.1 model downloaded successfully"
        else
            echo "❌ Failed to download llama3.1 model"
        fi
    fi
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created. You can modify it to customize settings."
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To run the job scraper:"
echo "1. Make sure Ollama is running: ollama serve"
echo "2. Run the scraper: python3 main.py"
echo ""
echo "The scraper will:"
echo "• Search for software engineering jobs"
echo "• Filter out senior/staff positions"
echo "• Analyze job descriptions with LLM"
echo "• Save suitable jobs to suitable_jobs.txt"

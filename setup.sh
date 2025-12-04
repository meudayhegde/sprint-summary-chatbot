#!/bin/bash

# Sprint Summary Chatbot - Quick Start Script

echo "🚀 Sprint Summary Chatbot - Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Python 3 is not installed!"; exit 1; }
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API key!"
    echo "   Open .env and set your LLM_PROVIDER and corresponding API key"
    echo ""
else
    echo ".env file already exists"
    echo ""
fi

echo "=================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API key"
echo "2. Run: python app.py"
echo "3. Open: http://localhost:8000"
echo ""
echo "To activate the virtual environment later:"
echo "  source venv/bin/activate"
echo ""

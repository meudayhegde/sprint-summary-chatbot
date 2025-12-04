#!/bin/bash

# Quick Start Script - Run this after setup
# Activates environment and starts the application

echo "🚀 Starting Sprint Summary Chatbot..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Using .env.example as template"
    cp .env.example .env
    echo ""
    echo "❌ Please edit .env and add your API key, then run this script again"
    exit 1
fi

# Check if API key is configured
if grep -q "your_openai_api_key_here" .env || grep -q "your_google_api_key_here" .env || grep -q "your_anthropic_api_key_here" .env; then
    echo "⚠️  Warning: API key appears to be unconfigured in .env"
    echo "   Please edit .env and add your actual API key"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "=================================="
echo "✅ Starting application..."
echo "=================================="
echo ""
echo "📍 Application will be available at: http://localhost:8000"
echo "📚 API Documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the application
python app.py

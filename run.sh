#!/bin/bash

echo "🚀 Starting RAG Chatbot Server..."
echo ""

# Check if .env exists and has API key
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please run: ./setup.sh first"
    exit 1
fi

# Check if API key is set
if grep -q "your_gemini_api_key_here" .env; then
    echo "❌ Error: Please set your Google Gemini API key in .env file"
    echo ""
    echo "Steps:"
    echo "1. Get API key from: https://makersuite.google.com/app/apikey"
    echo "2. Edit .env file and replace 'your_gemini_api_key_here'"
    echo "3. Run this script again"
    exit 1
fi

echo "✅ Configuration validated"
echo ""

# Run the application
python -m src.main

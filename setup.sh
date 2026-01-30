#!/bin/bash

echo "=============================================="
echo "RAG Chatbot Setup Script"
echo "=============================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
else
    echo "⚠️  .env file already exists"
fi

echo ""
echo "📝 Please set your Google Gemini API key in the .env file"
echo ""
echo "To get your API key:"
echo "1. Visit: https://makersuite.google.com/app/apikey"
echo "2. Create or copy your API key"
echo "3. Edit .env file and replace 'your_gemini_api_key_here' with your actual key"
echo ""
echo "Then run: python -m src.main"
echo ""
echo "=============================================="

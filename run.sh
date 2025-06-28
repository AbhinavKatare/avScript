#!/bin/bash

echo "🚀 Starting AVScript AI Chatbot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    ./setup.sh
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if MongoDB is running
echo "Checking MongoDB..."
if ! pgrep -x "mongod" > /dev/null; then
    echo "Starting MongoDB..."
    sudo systemctl start mongod || echo "Please start MongoDB manually"
fi

# Check if Ollama is running (optional)
echo "Checking Ollama..."
if command -v ollama &> /dev/null; then
    if ! pgrep -f "ollama" > /dev/null; then
        echo "Starting Ollama..."
        ollama serve &
        sleep 2
    fi
else
    echo "Ollama not found. Install from https://ollama.ai for better performance"
fi

# Create vector index if it doesn't exist
if [ ! -d "vector_index" ] || [ -z "$(ls -A vector_index)" ]; then
    echo "Creating vector index..."
    python backend/preprocess.py create
fi

# Run health check
echo "Running health check..."
python backend/health_check.py

# Start the application
echo "Starting AVScript AI..."
python backend/app.py

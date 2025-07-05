#!/bin/bash

# Check if Ollama is running, if not start it
if ! pgrep -x "ollama" > /dev/null
then
    echo "Starting Ollama..."
    ollama serve &
    # Wait a bit for Ollama to initialize
    sleep 5
else
    echo "Ollama is already running."
fi

# Start Open WebUI using docker-compose
echo "Starting Open WebUI..."
cd "$(dirname "$0")"
docker-compose up -d

echo "Services started successfully!"
echo "Open WebUI is available at: http://localhost:3000"

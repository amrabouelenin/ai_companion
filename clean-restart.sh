#!/bin/bash

echo "Stopping any running Open WebUI container..."
docker compose down

echo "Removing old volume..."
docker volume rm open-webui || true

echo "Starting Ollama if not already running..."
pgrep -x "ollama" > /dev/null || (echo "Starting Ollama..." && ollama serve &)
sleep 2  # Give Ollama a moment to start

echo "Starting Open WebUI with fresh configuration..."
docker compose up -d

echo "Waiting for container to initialize (30 seconds)..."
sleep 30

echo "Checking if Ollama is running..."
pgrep -x "ollama" > /dev/null && echo "Ollama is running" || echo "Ollama is NOT running"

echo "Checking container status..."
docker ps | grep open-webui

echo "You should now be able to access Open WebUI at http://localhost:8080"
echo "If you still cannot access it, try the following command to see detailed logs:"
echo "docker logs open-webui"

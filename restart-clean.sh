#!/bin/bash

echo "Stopping any running Open WebUI container..."
docker stop open-webui || true
docker rm open-webui || true

echo "Starting Ollama if not already running..."
pgrep -x "ollama" > /dev/null || (echo "Starting Ollama..." && ollama serve &)
sleep 2  # Give Ollama a moment to start

echo "Checking Ollama API accessibility..."
curl -s http://localhost:11434/api/version || echo "Warning: Ollama API not accessible at http://localhost:11434/api"

echo "Starting Open WebUI with fresh configuration..."
docker compose up -d

echo "Waiting for container to initialize (30 seconds)..."
sleep 30

echo "Checking container status..."
docker ps | grep open-webui

echo "Testing connection from container to host..."
docker exec open-webui curl -s http://host.docker.internal:11434/api/version || echo "Warning: Container cannot connect to Ollama API"

echo "You should now be able to access Open WebUI at http://localhost:3000"
echo "If you still cannot access it, try the following command to see detailed logs:"
echo "docker logs open-webui"

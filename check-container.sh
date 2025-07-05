#!/bin/bash

echo "Checking container status..."
docker ps -a | grep open-webui

echo -e "\nChecking container logs..."
docker logs open-webui

echo -e "\nChecking if Ollama is running..."
pgrep -x "ollama" > /dev/null && echo "Ollama is running" || echo "Ollama is NOT running"

echo -e "\nChecking Ollama API accessibility..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:11434/api/version || echo "Failed to connect to Ollama API"

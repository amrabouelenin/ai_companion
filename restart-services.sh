#!/bin/bash

echo "Stopping Open WebUI container..."
docker compose down

echo "Starting Open WebUI container with disabled health check..."
docker compose up -d

echo "Checking container status..."
docker ps | grep open-webui

echo "You should now be able to access Open WebUI at http://localhost:3000"
echo "If you still cannot access it, try the following command to see detailed logs:"
echo "docker logs open-webui"

# Local LLM Setup with Ollama and Open WebUI

This setup allows you to run Ollama locally with Open WebUI as a user interface.

## Prerequisites

- Docker and Docker Compose installed
- Ollama installed locally

## Setup Instructions

1. Make the start script executable:
   ```bash
   chmod +x start-llm-services.sh
   ```

2. Start both services (Ollama and Open WebUI):
   ```bash
   ./start-llm-services.sh
   ```

3. Access Open WebUI at: http://localhost:3000

## Services

- **Ollama**: Runs locally on your machine and serves the LLM API at port 11434
- **Open WebUI**: Runs in a Docker container and provides a web interface at port 3000

## Stopping the Services

To stop the Open WebUI container:
```bash
docker compose down
```

To stop Ollama, you can use:
```bash
pkill ollama
```

## Configuration

The docker-compose.yaml file contains the configuration for Open WebUI. You can modify it as needed.

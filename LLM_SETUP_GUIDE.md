# Local LLM Setup with Ollama and Open WebUI

## System Requirements
- Ubuntu 22.04 LTS or later
- Minimum 8GB RAM (16GB+ recommended)
- At least 10GB free disk space
- Docker installed
- Python 3.8+

## Installation Steps

### 1. Install Ollama
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
sudo systemctl start ollama
sudo systemctl enable ollama

# Verify installation
ollama --version
```

### 2. Download LLaMA 3 Model
```bash
# Download LLaMA 3 8B model (best for most systems)
ollama pull llama3:8b

# Verify model download
ollama list
```

### 3. Install and Configure Open WebUI
```bash
# Stop and remove any existing container
docker stop open-webui 2>/dev/null || true
docker rm open-webui 2>/dev/null || true

# Run Open WebUI container
docker run -d \
  -p 3000:8080 \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  --add-host=host.docker.internal:host-gateway \
  -e OLLAMA_API_BASE_URL=http://host.docker.internal:11434/api \
  ghcr.io/open-webui/open-webui:main


# Check container status
docker ps
```

## Accessing the Web Interface
1. Open your web browser
2. Navigate to: http://localhost:3000
3. Create an account or log in
4. Select the LLaMA 3 model from the model selector

## Troubleshooting

### If WebUI is not accessible:
1. Check container logs:
   ```bash
   docker logs open-webui
   ```
2. Verify port is open:
   ```bash
   ss -tulpn | grep 3000
   ```
3. Check container networking:
   ```bash
   docker inspect open-webui | grep -A 10 "NetworkSettings"
   ```

### If model is not responding:
1. Verify Ollama is running:
   ```bash
   curl http://localhost:11434/api/tags
   ```
2. Check model status:
   ```bash
   ollama list
   ```

## Performance Optimization (CPU-Only)
1. Reduce context length in model settings
2. Use smaller models (e.g., 7B instead of 13B)
3. Close other memory-intensive applications
4. Consider adding swap space if needed

## Maintenance

### Updating Components
```bash
# Update Ollama
sudo systemctl stop ollama
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl start ollama

# Update Open WebUI
docker pull ghcr.io/open-webui/open-webui:main
docker-compose down
docker-compose up -d
```

### Backup Your Data
```bash
# Backup Open WebUI data
docker run --rm -v open-webui:/source -v $(pwd):/backup alpine tar czf /backup/open-webui-backup-$(date +%Y%m%d).tar.gz -C /source .
```

## Common Issues

### Permission Denied Errors
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Port Already in Use
```bash
# Find and kill the process using the port
sudo lsof -i :3000
kill -9 <PID>
```

## Next Steps
- Try different models: `ollama pull llama2:13b`
- Explore advanced configuration options
- Set up authentication for production use
- Configure model parameters for better performance

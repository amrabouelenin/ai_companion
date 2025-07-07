import httpx
import json
from typing import Dict, Any, List, Optional

class LLMService:
    """Service for interacting with LLM models via Ollama."""
    
    def __init__(self, ollama_url: str):
        self.ollama_url = ollama_url
        # Use a smaller model that will respond faster
        self.default_model = "tinyllama:latest"
        # Track the current model (can be changed via API)
        self.current_model = self.default_model
        
    async def generate_response(self, 
                              prompt: str, 
                              system_prompt: str = "", 
                              model: Optional[str] = None,
                              temperature: float = 0.7,
                              max_tokens: int = 500) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The user's message
            system_prompt: Optional system prompt to guide the model's behavior
            model: Which Ollama model to use
            temperature: Creativity parameter (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        if not model:
            model = self.default_model
            
        try:
            print(f"Starting LLM request to {self.ollama_url} with model {model}...")
            
            # Try using the completion endpoint instead of chat
            # See: https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-completion
            full_prompt = ""
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n"
            full_prompt += prompt
            
            payload = {
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            }
            
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            # Longer timeout to accommodate larger models
            async with httpx.AsyncClient(timeout=60.0) as client:
                print(f"Sending POST request to {self.ollama_url}/api/generate...")
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload
                )
                print(f"Received response with status code {response.status_code}")
                
                if response.status_code != 200:
                    print(f"LLM Error: Status {response.status_code}, Response: {response.text}")
                    return "Sorry, I'm having trouble thinking right now."
                
                print("Parsing JSON response...")
                result = response.json()
                # generate endpoint returns 'response' field directly
                content = result.get("response", "")
                print(f"Got content of length: {len(content)}")
                return content
                
        except Exception as e:
            print(f"Error in LLM service: {str(e)}")
            import traceback
            traceback.print_exc()
            return "Sorry, I encountered an error while processing your request."
            
    async def get_available_models(self) -> List[str]:
        """
        Get a list of available models from Ollama.
        
        Returns:
            List of model names
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                print(f"{self.ollama_url}/api/tags")
                if response.status_code != 200:
                    return [self.default_model]
                    
                result = response.json()
                print(f"Available modelssss: {result.get('models', [])}")
                models = [model.get("name") for model in result.get("models", [])]
                return models if models else [self.default_model]
                
        except Exception as e:
            print(f"Error getting available models: {str(e)}")
            return [self.default_model]

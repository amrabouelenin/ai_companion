from typing import List, Dict, Any, Optional
import json
from services.llm_service import LLMService

class ModeManager:
    """Manages different companion modes and their behavior."""
    
    def __init__(self, available_modes: List[str], default_mode: str, llm_service: LLMService):
        self.available_modes = available_modes
        self.active_mode = default_mode
        self.llm_service = llm_service
        self._load_mode_configs()
        
    def _load_mode_configs(self):
        """Load configurations for each available mode."""
        self.mode_configs = {
            "general": {
                "name": "General Assistant",
                "description": "A helpful, friendly AI companion for everyday tasks and conversation.",
                "system_prompt": "You are a helpful and friendly AI companion. Your tone is warm and conversational. You assist with questions, provide information, and engage in pleasant conversation.",
                "temperature": 0.7,
                "model": "llama3",
                "id": "general"
            },
            "french_tutor": {
                "name": "French Tutor",
                "description": "A dedicated French language tutor to help you learn and practice French.",
                "system_prompt": "You are a French language tutor. Help the user learn French by teaching vocabulary, grammar, pronunciation, and cultural aspects. Respond in both French and English, providing translations and explanations. Adjust to the user's level. If the user speaks in French, provide gentle corrections if needed.",
                "temperature": 0.6,
                "model": "llama3",
                "id": "french_tutor"
            },
            "motivator": {
                "name": "Motivational Coach",
                "description": "An energetic motivator to help you stay focused and positive.",
                "system_prompt": "You are an enthusiastic motivational coach. Your tone is energetic, positive, and encouraging. Help the user stay motivated, set goals, overcome challenges, and celebrate achievements. Provide inspirational quotes and practical advice.",
                "temperature": 0.8,
                "model": "llama3",
                "id": "motivator"
            },
            "chill_buddy": {
                "name": "Chill Buddy",
                "id": "chill_buddy",
                "description": "A relaxed companion for casual conversation and entertainment.",
                "system_prompt": "You are a laid-back, chill companion. Your tone is casual, sometimes humorous, and always relaxed. You're here to chat, share interesting facts, tell jokes, discuss movies, music, or whatever the user wants to talk about in a low-pressure way.",
                "temperature": 0.9,
                "model": "llama3",
                
            }
        }
        
    def get_available_modes(self) -> List[Dict[str, Any]]:
        """
        Get information about all available modes.
        
        Returns:
            List of mode information dictionaries
        """
        modes = []
        for mode_id in self.available_modes:
            if mode_id in self.mode_configs:
                mode_info = {
                    "name": self.mode_configs[mode_id]["name"],
                    "description": self.mode_configs[mode_id]["description"],
                    "id": self.mode_configs[mode_id]["id"],
                    "active": mode_id == self.active_mode,
                    
                }
                modes.append(mode_info)
        return modes
        
    def set_active_mode(self, mode_id: str) -> None:
        """
        Set the active companion mode.
        
        Args:
            mode_id: ID of the mode to activate
            
        Raises:
            ValueError: If the mode is not available
        """
        # First try direct match with available_modes (for backward compatibility)
        if mode_id in self.available_modes:
            self.active_mode = mode_id
            return
            
        # Then try to find by id in mode configs
        for mode_key in self.available_modes:
            if mode_key in self.mode_configs and self.mode_configs[mode_key].get("id") == mode_id:
                self.active_mode = mode_key
                return
                
        # Mode not found
        raise ValueError(f"Mode with ID '{mode_id}' is not available")
            
        
    async def process_input(self, text: str, mode: str, user_id: str) -> str:
        """
        Process user input based on the selected mode.
        
        Args:
            text: User's input text
            mode: Mode to use for processing
            user_id: Identifier for the user
            
        Returns:
            Generated response
        """
        if mode not in self.mode_configs:
            # Fall back to default mode
            mode = "general"
            
        mode_config = self.mode_configs[mode]
        
        # Get the mode-specific system prompt
        system_prompt = mode_config["system_prompt"]
        temperature = mode_config.get("temperature", 0.7)
        model = mode_config.get("model", "llama3")
        
        # Process special modes with custom logic if needed
        if mode == "french_tutor":
            return await self._process_french_tutor_mode(text, system_prompt, temperature, model)
        else:
            # Default processing for other modes
            return await self.llm_service.generate_response(
                prompt=text,
                system_prompt=system_prompt,
                temperature=temperature,
                model=model
            )
            
    def get_active_system_prompt(self) -> str:
        """
        Get the system prompt for the currently active mode.
        
        Returns:
            The system prompt string for the active mode
        """
        if self.active_mode in self.mode_configs:
            return self.mode_configs[self.active_mode]["system_prompt"]
        else:
            # Fallback to general mode if active mode is not found
            return self.mode_configs["general"]["system_prompt"]
            
    async def _process_french_tutor_mode(self, text: str, system_prompt: str, temperature: float, model: str) -> str:
        """
        Special processing for French tutor mode.
        
        Args:
            text: User's input text
            system_prompt: System prompt for the model
            temperature: Temperature setting for the model
            model: Model to use
            
        Returns:
            Generated response with French learning enhancements
        """
        # Enhanced system prompt for French tutoring
        enhanced_prompt = system_prompt + "\n\n"
        enhanced_prompt += "Guidelines for your responses:\n"
        enhanced_prompt += "1. If the user asks a question in English, respond with both French and English translations\n"
        enhanced_prompt += "2. If the user speaks in French with errors, provide gentle corrections\n"
        enhanced_prompt += "3. Include pronunciation tips using phonetic notation when introducing new words\n"
        enhanced_prompt += "4. Occasionally introduce relevant cultural context about French-speaking regions\n"
        
        return await self.llm_service.generate_response(
            prompt=text,
            system_prompt=enhanced_prompt,
            temperature=temperature,
            model=model
        )

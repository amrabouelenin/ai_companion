import re
from typing import Dict, List, Tuple

class EmotionService:
    """Service for detecting and generating emotional expressions for the AI Companion."""
    
    def __init__(self):
        # Define emotion keywords for basic emotion detection
        self.emotion_keywords = {
            "happy": ["happy", "glad", "joy", "delighted", "excited", "fantastic", "wonderful", "amazing", "great", "pleased", "smile", "laugh", "yay"],
            "sad": ["sad", "unhappy", "upset", "disappointed", "sorry", "regret", "unfortunate", "depressed", "down", "blue", "tearful"],
            "angry": ["angry", "mad", "furious", "annoyed", "irritated", "frustrated", "upset", "rage", "temper", "outrage"],
            "confused": ["confused", "unsure", "unclear", "don't understand", "puzzled", "perplexed", "uncertain", "doubt", "wondering", "what?"],
            "surprised": ["surprised", "wow", "whoa", "amazing", "unbelievable", "incredible", "unexpected", "astonishing", "shocking"],
            "interested": ["interesting", "curious", "fascinated", "tell me more", "learning", "discovering", "exploring"],
            "bored": ["boring", "bored", "uninteresting", "tedious", "dull", "repetitive"],
            "thinking": ["thinking", "processing", "analyzing", "calculating", "considering", "let me think"]
        }
        
    def analyze_emotion(self, text: str) -> str:
        """
        Analyze text content to determine the most appropriate emotional response.
        
        Args:
            text: The text to analyze for emotional content
            
        Returns:
            The detected emotion (or default "neutral")
        """
        text_lower = text.lower()
        emotion_scores = {}
        
        # Score each emotion based on keyword matches
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            emotion_scores[emotion] = score
        
        # Find emotion with highest score
        max_score = max(emotion_scores.values()) if emotion_scores else 0
        if max_score > 0:
            # Get all emotions with the max score
            max_emotions = [e for e, s in emotion_scores.items() if s == max_score]
            return max_emotions[0]  # Return the first one if there are ties
            
        # Default to neutral if no strong emotions detected
        return "neutral"
    
    def detect_emotion(self, text: str) -> str:
        """
        Alias for analyze_emotion to maintain API compatibility.
        
        Args:
            text: The text to analyze for emotional content
            
        Returns:
            The detected emotion (or default "neutral")
        """
        return self.analyze_emotion(text)
        
    def get_emotion_expression(self, emotion: str) -> Dict[str, str]:
        """
        Get the appropriate expression for an emotion (for visual display).
        
        Args:
            emotion: The emotion to express
            
        Returns:
            A dictionary with display properties for the emotion
        """
        expressions = {
            "happy": {
                "emoji": "😊",
                "color": "#FFC107",  # Amber
                "animation": "bounce",
                "voice_modulation": "cheerful"
            },
            "sad": {
                "emoji": "😢",
                "color": "#2196F3",  # Blue
                "animation": "slow-pulse",
                "voice_modulation": "somber"
            },
            "angry": {
                "emoji": "😠",
                "color": "#F44336",  # Red
                "animation": "shake",
                "voice_modulation": "stern"
            },
            "confused": {
                "emoji": "🤔",
                "color": "#9C27B0",  # Purple
                "animation": "wobble",
                "voice_modulation": "uncertain"
            },
            "surprised": {
                "emoji": "😮",
                "color": "#FF9800",  # Orange
                "animation": "pop",
                "voice_modulation": "excited"
            },
            "interested": {
                "emoji": "🧐",
                "color": "#4CAF50",  # Green
                "animation": "pulse",
                "voice_modulation": "engaged"
            },
            "bored": {
                "emoji": "😴",
                "color": "#9E9E9E",  # Gray
                "animation": "slow-fade",
                "voice_modulation": "monotone"
            },
            "thinking": {
                "emoji": "💭",
                "color": "#3F51B5",  # Indigo
                "animation": "pulse-slow",
                "voice_modulation": "thoughtful"
            },
            "neutral": {
                "emoji": "😐",
                "color": "#607D8B",  # Blue Gray
                "animation": "none",
                "voice_modulation": "neutral"
            }
        }
        
        return expressions.get(emotion, expressions["neutral"])

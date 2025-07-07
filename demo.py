#!/usr/bin/env python3
"""
AI Companion Demo Script

This script demonstrates the end-to-end functionality of the AI Companion system.
It shows how to interact with the companion orchestrator API using different modes.
"""

import requests
import json
import time
import base64
import argparse
import os

BASE_URL = "http://localhost:8000"

def print_separator():
    """Print a separator line for better readability"""
    print("\n" + "="*80 + "\n")

def get_available_modes():
    """Retrieve available companion modes"""
    print("Retrieving available modes...")
    response = requests.get(f"{BASE_URL}/modes")
    
    if response.status_code == 200:
        modes = response.json()
        print("Available modes:")
        for mode in modes:
            active_status = "ACTIVE" if mode.get("active", False) else "inactive"
            print(f"  - {mode['name']}: {mode['description']} ({active_status})")
        return modes
    else:
        print(f"Error retrieving modes: {response.status_code}")
        print(response.text)
        return []

def set_mode(mode_name):
    """Set the active companion mode"""
    print(f"Setting mode to '{mode_name}'...")
    response = requests.post(f"{BASE_URL}/mode/{mode_name}")
    
    if response.status_code == 200:
        print(f"Mode successfully set to {mode_name}")
        return True
    else:
        print(f"Error setting mode: {response.status_code}")
        print(response.text)
        return False

def chat_with_companion(text, mode=None):
    """Send a text message to the companion"""
    print(f"Sending message: '{text}'")
    
    payload = {
        "text": text,
        "user_id": "demo_user"
    }
    
    if mode:
        payload["mode"] = mode
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("\nCompanion response:")
        print(f"Text: {result['text']}")
        print(f"Emotion: {result['emotion']}")
        print(f"Audio URL: {result['audio_url']}")
        return result
    else:
        print(f"Error chatting with companion: {response.status_code}")
        print(response.text)
        return None

def get_audio_response(audio_url):
    """Get audio response from the companion"""
    # Strip the query parameters from the URL and use proper POST request
    text = audio_url.split('text=')[1]
    # URL decode the text
    import urllib.parse
    text = urllib.parse.unquote(text)
    
    payload = {
        "text": text,
        "user_id": "demo_user"
    }
    
    print("Retrieving audio response...")
    response = requests.post(f"{BASE_URL}/text-to-speech", json=payload)
    
    if response.status_code == 200:
        # Save audio to file
        filename = f"response_{int(time.time())}.wav"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Audio response saved to {filename}")
        return filename
    else:
        print(f"Error retrieving audio: {response.status_code}")
        print(response.text)
        return None

def run_demo():
    """Run the full demo sequence"""
    print_separator()
    print("AI COMPANION DEMO")
    print_separator()
    
    # 1. Check available modes
    modes = get_available_modes()
    if not modes:
        print("No modes available. Exiting demo.")
        return
    
    print_separator()
    
    # 2. General mode conversation
    print("DEMO PART 1: General conversation")
    chat_result = chat_with_companion("Hello! Can you tell me a bit about yourself?")
    if chat_result:
        audio_file = get_audio_response(chat_result["audio_url"])
    
    print_separator()
    
    # 3. Switch to French tutor mode
    print("DEMO PART 2: French tutor mode")
    if set_mode("french_tutor"):
        chat_result = chat_with_companion("I'd like to learn some basic French greetings")
        if chat_result:
            audio_file = get_audio_response(chat_result["audio_url"])
    
    print_separator()
    
    # 4. Return to general mode but specify mode in request
    print("DEMO PART 3: Direct mode specification")
    chat_result = chat_with_companion("What's the weather like today?", mode="general")
    if chat_result:
        audio_file = get_audio_response(chat_result["audio_url"])
    
    print_separator()
    print("Demo complete! All AI Companion features have been tested.")
    print_separator()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Companion Demo")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for the companion orchestrator API")
    
    args = parser.parse_args()
    BASE_URL = args.url
    
    run_demo()

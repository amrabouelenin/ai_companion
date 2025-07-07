#!/usr/bin/env python3
import requests
import json
import os

# API endpoint
api_url = "http://localhost:8000/voice"

# Use a valid existing audio file
audio_file_path = "/home/amro/ai_companion/direct_speech.wav"
if not os.path.exists(audio_file_path):
    print(f"Error: Audio file not found at {audio_file_path}")
    exit(1)

print(f"Using audio file: {audio_file_path}")
print(f"Audio file size: {os.path.getsize(audio_file_path)} bytes")

# Send the request as multipart/form-data
print("Sending voice request to API...")
try:
    # Open the audio file for reading
    with open(audio_file_path, "rb") as audio_file:
        # Create form data with the audio file and other parameters
        files = {'audio_data': ('audio.wav', audio_file, 'audio/wav')}
        data = {
            'model': 'tinyllama:latest',  # Use the model we know is available
            'generate_audio': 'true'
        }
        
        # Send the request with both files and form data
        response = requests.post(api_url, files=files, data=data)
    
    # Check response
    if response.status_code == 200:
        result = response.json()
        print("\nAPI Response:")
        print(f"Status: Success (200)")
        print(f"Transcription: {result.get('text', 'No text returned')}")
        print(f"Response: {result.get('response_text', 'No response text returned')}")
        print(f"Audio URL: {result.get('audio_url', 'No audio URL returned')}")
        print(f"Emotion: {result.get('emotion', 'No emotion returned')}")
    else:
        print(f"\nAPI Error: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error occurred: {str(e)}")

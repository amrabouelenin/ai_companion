#!/usr/bin/env python3
import requests
import os
import json

# Whisper STT service URL
whisper_url = "http://localhost:9000"

# Use a valid existing audio file
audio_file_path = "/home/amro/ai_companion/direct_speech.wav"
if not os.path.exists(audio_file_path):
    print(f"Error: Audio file not found at {audio_file_path}")
    exit(1)

print(f"Using audio file: {audio_file_path}")
print(f"Audio file size: {os.path.getsize(audio_file_path)} bytes")

# Send the request directly to Whisper STT API
print("Sending direct request to Whisper STT API...")
try:
    # Open the audio file for reading
    with open(audio_file_path, "rb") as audio_file:
        # Create form data with the audio file and other parameters
        files = {'audio_file': ('audio.wav', audio_file, 'audio/wav')}
        data = {'task': 'transcribe'}
        
        # Send the request with both files and form data
        response = requests.post(f"{whisper_url}/asr", files=files, data=data)
    
    # Check response
    print(f"\nAPI Response Status: {response.status_code}")
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"Transcription: {result.get('text', 'No text returned')}")
        except json.JSONDecodeError:
            print(f"Response is not JSON: {response.text[:200]}...")
    else:
        print(f"Error: {response.text[:200]}...")

except Exception as e:
    print(f"Error occurred: {str(e)}")

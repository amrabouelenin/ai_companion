#!/usr/bin/env python3
import requests
import os
import argparse

def test_voice_endpoint(audio_file_path, server_url="http://localhost:8000"):
    """
    Test the /voice endpoint by sending an audio file
    
    Args:
        audio_file_path: Path to the audio file (WAV format recommended)
        server_url: URL of the orchestrator service
    """
    if not os.path.exists(audio_file_path):
        print(f"Error: Audio file {audio_file_path} does not exist")
        return False
    
    # Read audio file
    with open(audio_file_path, "rb") as f:
        audio_data = f.read()
    
    # Prepare request
    url = f"{server_url}/voice"
    payload = {
        "audio_data": audio_data,
        "user_id": "test_user",
        "mode": "general"
    }
    
    print(f"Sending audio file {audio_file_path} to {url}")
    print(f"Audio file size: {len(audio_data)} bytes")
    
    try:
        # Send request
        # The API expects a JSON with audio_data as base64 encoded bytes
        import base64
        
        # Convert binary data to base64 string
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        json_payload = {
            "audio_data": audio_base64,
            "user_id": "test_user",
            "mode": "general"
        }
        
        # Send JSON request
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=json_payload, headers=headers)
        
        # Print response
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Response JSON:")
            print(response.json())
            return True
        else:
            print(f"Error: {response.text}")
            return False
    
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the /voice endpoint with an audio file")
    parser.add_argument("audio_file", help="Path to audio file to send")
    parser.add_argument("--url", default="http://localhost:8000", help="URL of the orchestrator service")
    
    args = parser.parse_args()
    test_voice_endpoint(args.audio_file, args.url)

#!/usr/bin/env python3
"""
Test script for AI Companion Robot services.
This script tests the connectivity and basic functionality of all services.
"""
import os
import httpx
import json
import sys
from pathlib import Path
import subprocess
import asyncio
from services.llm_service import LLMService
from services.tts_service import TTSService
from modes.mode_manager import ModeManager

async def test_ollama_connection():
    """Test connection to Ollama service."""
    print("Testing connection to Ollama...")
    
    ollama_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{ollama_url.split('/api')[0]}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model.get("name") for model in models]
                print(f"✅ Connected to Ollama successfully!")
                print(f"   Available models: {', '.join(model_names) if model_names else 'No models found'}")
                return True
            else:
                print(f"❌ Failed to connect to Ollama: Status code {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Failed to connect to Ollama: {str(e)}")
        return False

async def test_mozillatts_service():
    """Test connectivity with MozillaTTS service."""
    print("\n" + "-" * 30)
    print("Testing MozillaTTS service...")
    print("-" * 30)
    
    tts_url = os.getenv("TTS_SERVICE_URL", "http://localhost:5002")
    print(f"\nTesting MozillaTTS service at {tts_url}...")
    
    try:
        async with httpx.AsyncClient() as client:
            # MozillaTTS uses MaryTTS-compatible /voices endpoint
            response = await client.get(f"{tts_url}/voices")
            print(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ MozillaTTS service is responding!")
                # Response is a text with each voice on a new line
                voices = [v for v in response.text.strip().split('\n') if v]
                print(f"Available voices: {', '.join(voices[:3])}..." if len(voices) > 3 else f"Available voices: {', '.join(voices)}")
                
                # Also test the TTS endpoint to verify we can generate speech
                tts_response = await client.get(
                    f"{tts_url}/api/tts", 
                    params={"text": "Hello world", "voice": voices[0]}
                )
                if tts_response.status_code == 200:
                    print("✅ TTS synthesis endpoint is working!")
                else:
                    print(f"❌ TTS synthesis endpoint failed: {tts_response.status_code}")
                return True
            else:
                print("❌ Failed to connect to MozillaTTS service")
                print(f"Response: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Error connecting to MozillaTTS service: {str(e)}")
        return False

async def test_whisper_stt():
    """Test connection to Whisper STT service."""
    print("\n" + "-" * 30)
    print("Testing Whisper STT Service")
    print("-" * 30)
    
    whisper_url = os.getenv("WHISPER_STT_URL", "http://localhost:9000")
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            # The Whisper API has a Swagger UI at /docs endpoint - check that directly
            docs_response = await client.get(f"{whisper_url}/docs")
            
            if docs_response.status_code == 200:
                print(f"✅ Connected to Whisper STT at {whisper_url} - API documentation available")
                return True
            
            # Fallback to the root endpoint - accept 200, 307 (redirect), or 404
            response = await client.get(f"{whisper_url}/")
            if response.status_code in [200, 307, 404]:
                # 307 typically redirects to the docs in FastAPI
                print(f"✅ Connected to Whisper STT at {whisper_url} (status: {response.status_code})")
                return True
            else:
                print(f"❌ Failed to connect to Whisper STT: Status code {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Failed to connect to Whisper STT: {str(e)}")
        return False

async def test_basic_conversation():
    """Test a basic conversation flow through the LLM service."""
    print("\nTesting basic conversation with LLM...")
    
    ollama_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api")
    print(f"Using Ollama URL: {ollama_url}")
    llm_service = LLMService(ollama_url)
    
    try:
        # Test with a simple prompt - using a very short prompt for faster response
        prompt = "Say hello in French"
        system_prompt = "You are a French tutor. Keep responses under 10 words."
        
        print("Sending request to LLM service...")
        
        try:
            print("Starting LLM request with 10 second timeout...")
            # Use a shorter timeout to avoid long waits during testing
            response = await asyncio.wait_for(
                llm_service.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model="fast-tinyllama:latest",  # Explicitly use faster model
                    temperature=0.7,
                    max_tokens=20  # Further reduced to make it even faster
                ),
                timeout=10  # Shorter timeout for testing
            )
            print("LLM request completed successfully")
            
            if response:
                print(f"✅ Successfully generated response from LLM!")
                print(f"   Sample response: \"{response[:100]}{'...' if len(response) > 100 else ''}\"")
                return True
            else:
                print("❌ Failed to generate response from LLM (empty response)")
                return False
                
        except asyncio.TimeoutError:
            print("❌ LLM request timed out after 15 seconds")
            return False
            
    except Exception as e:
        print(f"❌ Error testing conversation: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

async def test_mode_manager():
    """Test the Mode Manager functionality."""
    print("\nTesting Mode Manager...")
    
    try:
        ollama_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api")
        llm_service = LLMService(ollama_url)
        
        available_modes = ["general", "french_tutor", "motivator", "chill_buddy"]
        mode_manager = ModeManager(available_modes, "general", llm_service)
        
        modes = mode_manager.get_available_modes()
        if not modes:
            print("❌ Failed to get available modes")
            return False
            
        print(f"✅ Successfully loaded {len(modes)} modes!")
        for mode in modes:
            print(f"   - {mode['name']}: {mode['description'][:50]}...")
            
        return True
    except Exception as e:
        print(f"❌ Error testing Mode Manager: {str(e)}")
        return False

async def main():
    print("=" * 50)
    print("AI COMPANION ROBOT - SERVICE TESTS")
    print("=" * 50)
    
    # Set environment variables for local testing if they don't exist
    if not os.getenv("OLLAMA_API_URL"):
        os.environ["OLLAMA_API_URL"] = "http://localhost:11434/api"
    if not os.getenv("TTS_SERVICE_URL"):
        os.environ["TTS_SERVICE_URL"] = "http://localhost:5002" 
    if not os.getenv("WHISPER_STT_URL"):
        os.environ["WHISPER_STT_URL"] = "http://localhost:9000"
        
    # Test services
    ollama_ok = await test_ollama_connection()
    tts_ok = await test_mozillatts_service()
    whisper_ok = await test_whisper_stt()
    
    # Only test conversation if Ollama is working
    conversation_ok = False
    if ollama_ok:
        conversation_ok = await test_basic_conversation()
        
    # Test Mode Manager
    mode_manager_ok = await test_mode_manager()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"Ollama Connection: {'✅ PASSED' if ollama_ok else '❌ FAILED'}")
    print(f"Piper TTS Connection: {'✅ PASSED' if tts_ok else '❌ FAILED'}")
    print(f"Whisper STT Connection: {'✅ PASSED' if whisper_ok else '❌ FAILED'}")
    print(f"LLM Conversation: {'✅ PASSED' if conversation_ok else '❌ FAILED'}")
    print(f"Mode Manager: {'✅ PASSED' if mode_manager_ok else '❌ FAILED'}")
    
    all_passed = ollama_ok and tts_ok and whisper_ok and conversation_ok and mode_manager_ok
    
    print("\nOverall Status:", "✅ ALL TESTS PASSED!" if all_passed else "❌ SOME TESTS FAILED")
    print("\nNote: Failed tests may indicate that services are not running or not properly configured.")
    print("Make sure to start all services with 'docker compose up -d' before testing.")
    
    # Return exit code based on test results
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

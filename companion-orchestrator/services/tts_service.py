import os
import httpx
import logging
import urllib.parse
import re
import wave
import math
import struct
import io
import tempfile
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)

class TTSService:
    """Service for text-to-speech using MozillaTTS/Coqui TTS HTTP API."""

    def __init__(self):
        """Initialize the TTS service with environment variables."""
        # Try multiple potential TTS service URLs
        # This helps with DNS resolution issues in containerized environments
        primary_url = os.getenv("TTS_SERVICE_URL", "http://tts-service:5002")
        # Add direct IP address fallbacks for better container resolution
        fallback_urls = [
            "http://localhost:5002", 
            "http://tts-service.ai-network:5002",
            "http://172.20.0.4:5002",  # Direct IP address of TTS container
            "http://tts-service:5002"
        ]
        
        self.tts_url = primary_url
        self.fallback_urls = [url for url in fallback_urls if url != primary_url]
        
        logger.info(f"Initializing TTS service with URL: {self.tts_url} (fallbacks: {self.fallback_urls})")
        
        # Define default voices for each supported language
        self.default_voices = {
            "en": "cmu-bdl-hsmm",  # English male voice
            "fr": "upmc-pierre-hsmm"  # French male voice
        }
        
        # Connection will be verified on first request

    async def _verify_connection(self):
        """Try to verify connection to the TTS service and switch URLs if needed."""
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Try primary URL first
            try:
                logger.info(f"Testing connection to primary TTS URL: {self.tts_url}")
                response = await client.get(f"{self.tts_url}/voices")
                if response.status_code == 200:
                    logger.info(f"Successfully connected to TTS service at {self.tts_url}")
                    return True
            except Exception as e:
                logger.warning(f"Could not connect to primary TTS URL {self.tts_url}: {str(e)}")
            
            # Try fallback URLs if primary failed
            for url in self.fallback_urls:
                try:
                    logger.info(f"Testing connection to fallback TTS URL: {url}")
                    response = await client.get(f"{url}/voices")
                    if response.status_code == 200:
                        logger.info(f"Switching to working TTS service URL: {url}")
                        self.tts_url = url
                        return True
                except Exception as e:
                    logger.warning(f"Could not connect to fallback TTS URL {url}: {str(e)}")
            
            logger.error("Could not connect to any TTS service URL")
            return False
        
    async def text_to_speech(self, text: str, language: Optional[str] = None):
        """Convert text to speech using MozillaTTS API and return binary audio data.
        
        Args:
            text: The text to convert to speech
            language: Optional language code to use (e.g., "en" or "fr")
            
        Returns:
            Binary audio data or fallback audio if conversion failed
        """
        if not text:
            logger.warning("Empty text provided to TTS service")
            return self._generate_fallback_audio()
            
        try:
            # First verify connection to TTS service
            connection_ok = await self._verify_connection()
            if not connection_ok:
                logger.error("Failed to connect to any TTS service URL")
                return self._generate_fallback_audio()
                
            # Auto-detect language based on text content if voice not specified
            voice = None
            if language and language.lower().startswith("fr"):
                voice = self.default_voices["fr"]
                logger.info(f"Using French voice: {voice}")
            else:
                if self._is_mostly_french(text):
                    voice = self.default_voices["fr"]
                    logger.info(f"Detected French text, using voice: {voice}")
                else:
                    voice = self.default_voices["en"]
                    logger.info(f"Using default English voice: {voice}")
            
            # Split long text into smaller chunks that the TTS model can handle
            # This helps avoid the "kernel size can't be greater than actual input size" error
            max_chunk_length = 200  # Maximum characters per chunk
            sentences = self._split_into_sentences(text)
            chunks = self._create_chunks(sentences, max_chunk_length)
            
            logger.info(f"Processing {len(chunks)} TTS chunks")
            
            # Process chunks and get audio files for each
            temp_files = []
            async with httpx.AsyncClient(timeout=60.0) as client:
                for i, chunk in enumerate(chunks):
                    try:
                        chunk_audio = await self._process_tts_chunk(chunk, voice, client)
                        if chunk_audio:
                            # Save each chunk to a temporary file
                            fd, temp_path = tempfile.mkstemp(suffix=f".{i}.wav")
                            os.write(fd, chunk_audio)
                            os.close(fd)
                            temp_files.append(temp_path)
                            logger.info(f"Generated audio for chunk {i+1}, saved to {temp_path}")
                        else:
                            logger.warning(f"Failed to generate audio for chunk {i+1}")
                    except Exception as e:
                        logger.error(f"Error processing chunk {i+1}: {str(e)}")
            
            # If we couldn't generate any audio, return fallback
            if not temp_files:
                logger.warning("No audio data generated, using fallback")
                return self._generate_fallback_audio()
            
            # Properly combine WAV files using FFmpeg if we have multiple chunks
            if len(temp_files) > 1:
                try:
                    output_file = tempfile.mktemp(suffix=".combined.wav")
                    # Create a file list for FFmpeg
                    list_file = tempfile.mktemp(suffix=".list")
                    with open(list_file, "w") as f:
                        for temp_file in temp_files:
                            f.write(f"file '{temp_file}'\n")
                    
                    # Use FFmpeg to concatenate the audio files properly
                    cmd = [
                        "ffmpeg", "-f", "concat", "-safe", "0", 
                        "-i", list_file, "-c", "copy", output_file
                    ]
                    logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
                    subprocess.run(cmd, check=True, capture_output=True)
                    
                    # Read the combined file
                    with open(output_file, "rb") as f:
                        combined_audio = f.read()
                    
                    # Clean up temporary files
                    for temp_file in temp_files:
                        os.remove(temp_file)
                    os.remove(list_file)
                    os.remove(output_file)
                    
                    return combined_audio
                except Exception as e:
                    logger.error(f"Error combining audio chunks: {str(e)}")
                    # If concatenation fails, try to return the first chunk at least
                    if temp_files:
                        with open(temp_files[0], "rb") as f:
                            single_chunk = f.read()
                        # Clean up temp files
                        for temp_file in temp_files:
                            try:
                                os.remove(temp_file)
                            except:
                                pass
                        return single_chunk
                    return self._generate_fallback_audio()
            elif len(temp_files) == 1:
                # Just one chunk, read it directly
                with open(temp_files[0], "rb") as f:
                    audio_data = f.read()
                os.remove(temp_files[0])
                return audio_data
            else:
                return self._generate_fallback_audio()
            
        except Exception as e:
            logger.error(f"Error in TTS service: {str(e)}")
            return self._generate_fallback_audio()
    
    async def _process_tts_chunk(self, text: str, voice: str, client):
        """Process a single chunk of text through TTS service"""
        try:
            # Prepare request payload with text and voice
            params = {
                "text": text,
                "voice": voice
            }
            
            # Use MozillaTTS API to generate speech
            logger.info(f"Requesting TTS for text: '{text[:30]}...' with voice {voice}")
            response = await client.get(f"{self.tts_url}/api/tts", params=params)
            
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"TTS API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing TTS chunk: {str(e)}")
            return None
            
    def _split_into_sentences(self, text: str):
        """Split text into sentences for better TTS chunking"""
        text = text.replace('\n', '. ')
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _create_chunks(self, sentences: list, max_length: int):
        """Create chunks of text from sentences that don't exceed max_length"""
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If this sentence alone is too long, split it further
            if len(sentence) > max_length:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                
                # Split long sentence by phrases (comma, semicolon, etc.)
                phrases = re.split(r'(?<=[:;,])\s+', sentence)
                for phrase in phrases:
                    if len(phrase) > max_length:
                        # If even a phrase is too long, split by word boundaries
                        words = phrase.split()
                        temp = ""
                        for word in words:
                            if len(temp) + len(word) + 1 > max_length:
                                chunks.append(temp)
                                temp = word
                            else:
                                temp = temp + " " + word if temp else word
                        if temp:
                            chunks.append(temp)
                    else:
                        # Add phrase if it fits in a chunk
                        if len(current_chunk) + len(phrase) + 2 > max_length:
                            chunks.append(current_chunk)
                            current_chunk = phrase
                        else:
                            current_chunk = current_chunk + ", " + phrase if current_chunk else phrase
            else:
                # Add sentence if it fits in current chunk
                if len(current_chunk) + len(sentence) + 2 > max_length:
                    chunks.append(current_chunk)
                    current_chunk = sentence
                else:
                    current_chunk = current_chunk + ". " + sentence if current_chunk else sentence
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
    
    def _generate_fallback_audio(self):
        """Generate a minimal fallback audio in case TTS fails"""
        logger.warning("Using fallback audio")
        
        # Generate a very simple beep sound instead of empty WAV
        # Create a basic sine wave tone (440 Hz, 0.5 seconds)
        sample_rate = 8000  # 8kHz
        duration = 0.5      # 0.5 seconds
        frequency = 440     # 440 Hz (A4)
        amplitude = 32767 / 2  # Half max amplitude for 16-bit
        
        # Generate samples
        num_samples = int(duration * sample_rate)
        samples = []
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            # Simple sine wave with fade in/out
            if i < num_samples / 10:  # Fade in
                fade = i / (num_samples / 10)
            elif i > num_samples * 9 / 10:  # Fade out
                fade = (num_samples - i) / (num_samples / 10)
            else:
                fade = 1.0
            sample = int(amplitude * fade * math.sin(2 * math.pi * frequency * t))
            samples.append(sample)
        
        # Pack samples into a binary string
        packed_samples = struct.pack('<{}h'.format(len(samples)), *samples)
        
        # Create WAV file in memory
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes (16 bits)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(packed_samples)
        
        # Get the WAV file as bytes
        buffer.seek(0)
        return buffer.read()
    
    def _is_mostly_french(self, text: str):
        """Heuristic to detect if a text is mostly French."""
        french_words = ["le", "la", "les", "un", "une", "des", "et", "ou", "je", "tu", "il", "elle", 
                       "nous", "vous", "ils", "elles", "être", "avoir", "faire", "aller", "bonjour", 
                       "merci", "s'il", "vous", "plaît"]
        
        words = text.lower().split()
        french_count = sum(1 for word in words if word in french_words)
        
        # If more than 25% of recognized words are French, use French voice
        return french_count > 0 and french_count / len(words) > 0.25 if words else False

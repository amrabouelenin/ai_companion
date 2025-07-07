import httpx
import base64
import os
import wave
import io
import struct
from typing import Optional, Dict, Any, Tuple
import subprocess
import tempfile

class STTService:
    """Service for speech-to-text conversion using Whisper."""
    
    def __init__(self, whisper_url: str):
        self.whisper_url = whisper_url
        
    def _check_wav_header(self, audio_data: bytes) -> Tuple[bool, str]:
        """
        Check if the audio data has a valid WAV header.
        Returns (is_valid, message)
        """
        try:
            # Check for minimum length for WAV header (44 bytes)
            if len(audio_data) < 44:
                return False, f"Audio data too short ({len(audio_data)} bytes)"
                
            # Check for RIFF header
            if audio_data[0:4] != b'RIFF':
                return False, "No RIFF header found"
                
            # Check for WAVE format
            if audio_data[8:12] != b'WAVE':
                return False, "Not a WAVE format"
                
            # Check for fmt chunk
            if audio_data[12:16] != b'fmt ':
                return False, "No fmt chunk found"
                
            return True, "Valid WAV header"
        except Exception as e:
            return False, f"Error checking WAV header: {str(e)}"
            
    def _convert_audio_to_wav(self, audio_data: bytes) -> bytes:
        """
        Convert audio data to WAV format using FFmpeg
        This handles various input formats including webm/opus from browsers
        
        Args:
            audio_data: The audio data in any format
            
        Returns:
            Audio data in WAV format
        """
        # First, check if it's already a valid WAV file
        if len(audio_data) >= 44 and audio_data[:4] == b'RIFF' and audio_data[8:12] == b'WAVE':
            print("Audio validation: Already a valid WAV file")
            return audio_data
            
        print("Audio format needs conversion: Not a valid WAV file")
        
        # Create temporary files for input and output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".audio") as temp_in_file:
            temp_in_path = temp_in_file.name
            temp_in_file.write(audio_data)
            
        temp_out_path = temp_in_path + ".wav"
        
        try:
            # Use FFmpeg to convert the audio to WAV format with enhanced parameters
            print(f"Converting audio to WAV format using FFmpeg: {temp_in_path} -> {temp_out_path}")
            cmd = [
                "ffmpeg",
                "-y",                    # Overwrite output without asking
                "-i", temp_in_path,     # Input file
                "-acodec", "pcm_s16le", # Convert to 16-bit PCM
                "-ar", "16000",         # 16kHz sample rate (ideal for Whisper)
                "-ac", "1",             # Mono (Whisper works best with mono)
                "-af", "highpass=f=50, lowpass=f=8000, volume=1.5",  # Audio filtering to enhance speech
                "-q:a", "0",            # Best audio quality
                temp_out_path           # Output file
            ]
            
            # Run FFmpeg command
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False  # Don't raise exception on non-zero exit
            )
            
            if process.returncode != 0:
                print(f"FFmpeg error: {process.stderr.decode()}")
                # If conversion fails, fall back to adding a basic WAV header
                return self._add_wav_header(audio_data)
                
            # Read the converted WAV file
            with open(temp_out_path, 'rb') as f:
                wav_data = f.read()
                
            print(f"Conversion successful. WAV size: {len(wav_data)} bytes")
            return wav_data
            
        except Exception as e:
            print(f"Error during audio conversion: {str(e)}")
            # Fall back to adding a basic WAV header
            return self._add_wav_header(audio_data)
            
        finally:
            # Clean up temporary files
            try:
                if os.path.exists(temp_in_path):
                    os.unlink(temp_in_path)
                if os.path.exists(temp_out_path):
                    os.unlink(temp_out_path)
            except Exception as e:
                print(f"Error cleaning up temp files: {str(e)}")
                
    async def speech_to_text(self, audio_data: bytes, language: Optional[str] = None) -> str:
        """
        Convert speech to text using Whisper.
        
        Args:
            audio_data: Raw audio data bytes
            language: Optional language code (e.g., 'en', 'fr')
            
        Returns:
            Transcribed text
        """
        try:
            # Log initial audio size and info
            print(f"Received audio data: {len(audio_data)} bytes")
            
            # Convert audio to WAV format (handles webm/opus from browsers)
            wav_audio_data = self._convert_audio_to_wav(audio_data)
            
            # Print binary header data for debugging (first 16 bytes)
            if len(wav_audio_data) >= 16:
                header_hex = ' '.join(f'{b:02x}' for b in wav_audio_data[:16])
                print(f"Audio header (hex): {header_hex}")
                try:
                    header_ascii = ''.join(chr(b) if 32 <= b < 127 else '.' for b in wav_audio_data[:16])
                    print(f"Audio header (ascii): {header_ascii}")
                except:
                    pass
            
            # Create a temporary wav file from the converted audio data
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(wav_audio_data)
                temp_file_path = temp_file.name
                
            print(f"Created temporary file: {temp_file_path}")
            
            # Prepare the multipart form-data request
            files = {
                'audio_file': ("audio.wav", open(temp_file_path, 'rb'), 'audio/wav')
            }
            
            # Add other parameters
            data = {
                'task': 'transcribe'
            }
            
            # Add language parameter if specified
            if language:
                data['language'] = language
                
            print(f"Sending request to Whisper STT at {self.whisper_url}/asr")
            async with httpx.AsyncClient(timeout=60.0) as client:  # Increased timeout
                response = await client.post(
                    f"{self.whisper_url}/asr",
                    files=files,
                    data=data
                )
                
                # Clean up the temporary file
                try:
                    os.unlink(temp_file_path)
                    print(f"Deleted temporary file: {temp_file_path}")
                except Exception as e:
                    print(f"Error deleting temporary file: {str(e)}")
                
                if response.status_code != 200:
                    print(f"STT Error: {response.status_code} - {response.text}")
                    return ""
                
                # Try to parse as JSON first
                try:
                    result = response.json()
                    text = result.get("text", "")
                    print(f"Successfully transcribed audio: '{text[:50]}...' ({len(text)} chars)")
                    return text
                except Exception as json_error:
                    # If not JSON, treat the response as plain text
                    print(f"Response is not JSON, treating as plain text. Error: {str(json_error)}")
                    response_text = response.text.strip()
                    if response_text:
                        print(f"Plain text response: {response_text[:50]}...")
                        return response_text
                    return ""
        except Exception as e:
            print(f"Error in speech_to_text: {str(e)}")
            return ""
                
    def _add_wav_header(self, audio_data: bytes) -> bytes:
        """
        Add a basic WAV header to raw audio data
        This is a fallback method when FFmpeg conversion fails
        
        Args:
            audio_data: The raw audio data
            
        Returns:
            Audio data with WAV header
        """
        print("Falling back to adding basic WAV header")
        
        # Create a minimal WAV header for 16-bit PCM mono at 16kHz
        # RIFF header
        wav_header = bytearray()
        wav_header.extend(b'RIFF')
        wav_header.extend((len(audio_data) + 36).to_bytes(4, byteorder='little'))  # File size - 8
        wav_header.extend(b'WAVE')
        
        # Format chunk
        wav_header.extend(b'fmt ')
        wav_header.extend((16).to_bytes(4, byteorder='little'))  # Chunk size
        wav_header.extend((1).to_bytes(2, byteorder='little'))    # Format = PCM
        wav_header.extend((1).to_bytes(2, byteorder='little'))    # Channels = 1
        wav_header.extend((16000).to_bytes(4, byteorder='little'))  # Sample rate
        wav_header.extend((32000).to_bytes(4, byteorder='little'))  # Byte rate
        wav_header.extend((2).to_bytes(2, byteorder='little'))    # Block align
        wav_header.extend((16).to_bytes(2, byteorder='little'))   # Bits per sample
        
        # Data chunk
        wav_header.extend(b'data')
        wav_header.extend((len(audio_data)).to_bytes(4, byteorder='little'))  # Data size
        
        # Combine header with audio data
        wav_data = wav_header + audio_data
        print(f"Created WAV file with basic header, size: {len(wav_data)} bytes")
        
        return wav_data
            
    async def detect_language(self, audio_data: bytes) -> str:
        """
        Detect the language of the audio using Whisper.
        
        Args:
            audio_data: Raw audio data bytes
            
        Returns:
            Detected language code
        """
        try:
            # Encode audio data as base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            payload = {
                "audio": audio_base64,
                "task": "language_detection"
            }
                
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.whisper_url}/detect-language",
                    json=payload
                )
                
                if response.status_code != 200:
                    print(f"Language detection error: {response.text}")
                    return "en"  # Default to English
                    
                result = response.json()
                return result.get("detected_language", "en")
                
        except Exception as e:
            print(f"Error in language detection: {str(e)}")
            return "en"  # Default to English

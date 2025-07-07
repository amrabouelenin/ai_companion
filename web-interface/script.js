/**
 * AI Companion Voice Chat Interface
 * Main JavaScript for handling voice input/output and API communication
 */

// Configuration
// The API_BASE_URL may need to be changed depending on how the app is accessed
let API_BASE_URL = 'http://localhost:8000'; // Default to localhost for direct browser access

// Check if we're running inside a Docker container
// If so, we might need to use the service name instead of localhost
if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    console.log('Debug - Not running on localhost, using window.location.origin');
    API_BASE_URL = window.location.origin;
}

// You can override the API_BASE_URL by uncommenting and editing this line:
//const API_BASE_URL = 'http://localhost:8000';  // Updated to use localhost:8000

console.log('Debug - Using API_BASE_URL:', API_BASE_URL);

const API_ENDPOINTS = {
    chat: '/chat',
    textToSpeech: '/text-to-speech',
    voice: '/voice',
    modes: '/modes',
    setMode: '/mode',
    models: '/models',     // New endpoint for fetching available models
    setModel: '/model'     // New endpoint for setting the active model
};

console.log('Debug - API endpoints:', API_ENDPOINTS);

// DOM Elements
const elements = {
    messageContainer: document.getElementById('messages'),
    recordButton: document.getElementById('record-button'),
    textInput: document.getElementById('text-input'),
    sendButton: document.getElementById('send-button'),
    modeSelect: document.getElementById('mode-select'),
    modelSelect: document.getElementById('model-select'),
    voiceResponseToggle: document.getElementById('voice-response-toggle'),
    statusIndicator: document.getElementById('status'),
    emotionIndicator: document.getElementById('emotion')
};

// State
const state = {
    recording: false,
    audioContext: null,
    mediaRecorder: null,
    audioChunks: [],
    currentMode: 'general',
    currentModel: '',
    availableModes: [],
    availableModels: [],
    useVoiceResponse: true
};

// Emotion mapping
const emotionIcons = {
    happy: '😊',
    sad: '😢',
    neutral: '😐',
    excited: '😃',
    confused: '🤔',
    surprised: '😮'
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    setupEventListeners();
    await Promise.all([
        loadAvailableModes(),
        loadAvailableModels()
    ]);
    
    // Initialize voice response toggle from state
    elements.voiceResponseToggle.checked = state.useVoiceResponse;
    updateStatusMessage('Ready to chat');
}

function setupEventListeners() {
    // Mode selection
    elements.modeSelect.addEventListener('change', async (e) => {
        const selectedMode = e.target.value;
        console.log('Selected mode:', selectedMode);
        await setCompanionMode(selectedMode);
    });
    console.log('Mode selection event listener set up');
    
    // Model selection
    elements.modelSelect.addEventListener('change', async (e) => {
        const selectedModel = e.target.value;
        await setModel(selectedModel);
    });
    
    // Voice response toggle
    elements.voiceResponseToggle.addEventListener('change', (e) => {
        state.useVoiceResponse = e.target.checked;
        console.log('Voice response', state.useVoiceResponse ? 'enabled' : 'disabled');
    });
    
    // Record button
    elements.recordButton.addEventListener('click', toggleRecording);
    
    // Send button
    elements.sendButton.addEventListener('click', sendTextMessage);
    
    // Text input - send on Enter key
    elements.textInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault(); // Prevent newline
            sendTextMessage();
        }
    });
}

async function loadAvailableModes() {
    try {
        updateStatusMessage('Loading available modes...');
        const url = `${API_BASE_URL}${API_ENDPOINTS.modes}`;
        console.log('Debug - Fetching modes from URL:', url);
        console.log('Debug - API_BASE_URL:', API_BASE_URL);
        console.log('Debug - API_ENDPOINTS.modes:', API_ENDPOINTS.modes);
        
        const response = await fetch(url);
        
        console.log('Debug - Mode response status:', response.status);
        console.log('Debug - Mode response headers:', [...response.headers.entries()]);
        
        if (!response.ok) {
            console.error(`Error loading modes: ${response.status} ${response.statusText}`);
            throw new Error(`Failed to load modes: ${response.status} ${response.statusText}`);
        }
        
        const responseText = await response.text();
        console.log('Debug - Raw response text:', responseText);
        
        let data;
        try {
            data = JSON.parse(responseText);
            console.log('Debug - Parsed mode data:', data);
        } catch (parseError) {
            console.error('Debug - Failed to parse mode data as JSON:', parseError);
            throw new Error('Invalid JSON response from modes endpoint');
        }
        
        // Check data structure
        console.log('Debug - Is data an array?', Array.isArray(data));
        console.log('Debug - Does data have modes property?', data && typeof data === 'object' && 'modes' in data);
        
        state.availableModes = Array.isArray(data) ? data : data.modes || [];
        console.log('Debug - Final available modes:', state.availableModes);
        
        // Populate select options
        elements.modeSelect.innerHTML = '';
        state.availableModes.forEach(mode => {
            console.log('Debug - Adding mode option:', mode);
            const option = document.createElement('option');
            option.value = mode.id;
            option.textContent = mode.name;
            if (mode.active) {
                option.selected = true;
                state.currentMode = mode.id;
            }
            elements.modeSelect.appendChild(option);
        });
        
        updateStatusMessage('Modes loaded');
    } catch (error) {
        console.error('Error loading modes:', error);
        updateStatusMessage('Error loading modes');
    }
}

async function loadAvailableModels() {
    try {
        updateStatusMessage('Loading available models...');
        console.log('Debug - Fetching available models from API');
        
        // Attempt to fetch available models from the backend
        // This endpoint may need to be implemented on the backend
        const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.models}`)
            .catch(err => {
                console.warn('Models endpoint not implemented yet:', err);
                // Return a mock response for now
                return new Response(JSON.stringify([
                    { id: 'llama2', name: 'Llama 2' },
                    { id: 'tinyllama', name: 'Tiny Llama' },
                    { id: 'mistral', name: 'Mistral' }
                ]));
            });
        
        if (!response.ok) {
            console.warn(`Models endpoint returned ${response.status}. Using default models.`);
            // Fallback to default models if the endpoint isn't available
            state.availableModels = [
                { id: 'llama2', name: 'Llama 2' },
                { id: 'tinyllama', name: 'Tiny Llama' },
                { id: 'mistral', name: 'Mistral' }
            ];
        } else {
            const data = await response.json();
            console.log('Debug - Available models:', data);
            
            if (data && Array.isArray(data)) {
                state.availableModels = data;
            }
        }
        
        // Populate select element
        elements.modelSelect.innerHTML = '';
        
        state.availableModels.forEach(model => {
            const option = document.createElement('option');
            option.value = model.id;
            option.textContent = model.name;
            elements.modelSelect.appendChild(option);
        });
        
        // Select the first model by default
        if (state.availableModels.length > 0) {
            state.currentModel = state.availableModels[0].id;
            elements.modelSelect.value = state.currentModel;
        }
        
        console.log('Debug - Selected model:', state.currentModel);
    } catch (error) {
        console.error('Error loading models:', error);
        // Add a default model if we couldn't load any
        elements.modelSelect.innerHTML = '<option value="default">Default Model</option>';
        state.currentModel = 'default';
    }
}

async function setCompanionMode(modeId) {
    try {
        if (!modeId) {
            console.error('Mode ID is undefined or empty');
            updateStatusMessage('Error: Invalid mode selected');
            return;
        }
        
        console.log(`Setting mode to: ${modeId}`);
        updateStatusMessage(`Switching to ${modeId} mode...`);
        
        // Use the correct endpoint format with the mode ID
        const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.setMode}/${modeId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`Failed to set mode: ${response.status}`);
        }
        
        console.log(`Mode switched to ${modeId}`);
        state.currentMode = modeId;
        updateStatusMessage(`Now in ${modeId} mode`);
        
        // Add system message about mode change
        const modeName = state.availableModes.find(m => m.name === modeId)?.display_name || modeId;
        addSystemMessage(`Switched to ${modeName} mode.`);
    } catch (error) {
        console.error('Error setting mode:', error);
        updateStatusMessage('Failed to switch mode');
        addSystemMessage(`Failed to switch to ${modeId} mode. Please try again.`);
    }
}

async function setModel(modelId) {
    try {
        updateStatusMessage(`Setting model to ${modelId}...`);
        updateStatusMessage(`Switching to ${modelId} model...`);
        
        // Use the correct endpoint format with path parameter
        const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.setModel}/${modelId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        }).catch(err => {
            console.warn('Model switching endpoint error:', err);
            // Return a mock success response for now
            return new Response(JSON.stringify({ status: 'success' }));
        });
        
        if (!response.ok) {
            throw new Error(`Failed to set model: ${response.status} ${response.statusText}`);
        }
        
        console.log(`Model switched to ${modelId}`);
        state.currentModel = modelId;
        updateStatusMessage(`Now using ${modelId} model`);
        
        // Add system message about model change
        const modelName = state.availableModels.find(m => m.id === modelId)?.name || modelId;
        addSystemMessage(`Switched to ${modelName} model.`);
    } catch (error) {
        console.error('Error setting model:', error);
        updateStatusMessage('Failed to switch model');
        addSystemMessage(`Failed to switch to the selected model. Please try again.`);
    }
}

// Recording functions
async function toggleRecording() {
    if (state.recording) {
        stopRecording();
    } else {
        await startRecording();
    }
}

async function startRecording() {
    try {
        // Request microphone access
        updateStatusMessage('Requesting microphone access...');
        
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
            .catch(error => {
                if (error.name === 'NotAllowedError') {
                    throw new Error('Microphone access denied by user');
                } else if (error.name === 'NotFoundError') {
                    throw new Error('No microphone found on your device');
                } else {
                    throw error; // Rethrow other errors
                }
            });
        
        // Create audio context
        state.audioContext = new AudioContext();
        
        // Create media recorder with specific MIME type for proper WAV format
        const options = { 
            mimeType: 'audio/webm', // Use webm which is well-supported
            audioBitsPerSecond: 16000 // Match Whisper's expected sample rate
        };
        
        try {
            state.mediaRecorder = new MediaRecorder(stream, options);
            console.log("Using audio/webm format for recording");
        } catch (e) {
            // Fallback if audio/webm isn't supported
            console.warn("audio/webm not supported, using default format", e);
            state.mediaRecorder = new MediaRecorder(stream);
        }
        
        // Start recording
        state.audioChunks = [];
        state.mediaRecorder.start();
        
        // Update UI
        state.recording = true;
        elements.recordButton.classList.add('recording');
        elements.recordButton.innerHTML = '<i class="fas fa-stop"></i>';
        updateStatusMessage('Recording... Click to stop');
        
        // Set up data handler
        state.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                state.audioChunks.push(event.data);
            }
        };
        
        // Set up stop handler
        state.mediaRecorder.onstop = handleRecordingStop;
        
        // Add timeout for maximum recording length (60 seconds)
        setTimeout(() => {
            if (state.recording) {
                stopRecording();
                addSystemMessage('Recording automatically stopped after 60 seconds.');
            }
        }, 60000);
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        updateStatusMessage('Error accessing microphone');
        addSystemMessage(`Microphone error: ${error.message || 'Could not access your microphone. Please check your browser permissions.'}`);
    }
}

function stopRecording() {
    if (state.mediaRecorder && state.recording) {
        state.mediaRecorder.stop();
        state.recording = false;
        elements.recordButton.classList.remove('recording');
        updateStatusMessage('Processing audio...');
    }
}

async function handleRecordingStop() {
    try {
        // Create audio blob with the correct MIME type from our recorder
        // Using the same MIME type that was used for recording (webm or default)
        const mimeType = state.mediaRecorder.mimeType || 'audio/webm';
        console.log(`Creating audio blob with MIME type: ${mimeType}`);
        
        const audioBlob = new Blob(state.audioChunks, { type: mimeType });
        
        // Convert the blob to a format Whisper can handle if needed
        console.log(`Audio blob size: ${audioBlob.size} bytes`);
        
        // Send the blob directly to API - no conversion needed
        await sendVoiceMessage(audioBlob);
    } catch (error) {
        console.error('Error processing recording:', error);
        updateStatusMessage('Error processing recording');
    }
}

// Chat functions
async function sendTextMessage() {
    const text = elements.textInput.value.trim();
    
    if (!text) return;
    
    // Clear input
    elements.textInput.value = '';
    
    // Add user message to UI
    addUserMessage(text);
    
    // Send to API
    try {
        await sendMessage(text);
    } catch (error) {
        console.error('Error sending message:', error);
        updateStatusMessage('Error sending message');
    }
}

async function sendVoiceMessage(audioBlob) {
    try {
        // Update status
        updateStatusMessage('Processing speech...');
        console.log('Debug - Starting voice recognition with audio blob size:', audioBlob.size);
        
        // Check if audio data is reasonably sized (not too small to be meaningful)
        if (audioBlob.size < 1000) {
            console.warn('Audio data seems too small, might not contain speech');
            updateStatusMessage('Audio recording too short');
            addSystemMessage('The audio recording was too short. Please try speaking longer or closer to the microphone.');
            return;
        }
        
        // Create AbortController to handle timeouts
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
            console.log('STT request timeout reached, aborting...');
            controller.abort('STT request timeout');
        }, 60000); // 60-second timeout for STT (increased from 30s)
        
        console.log(`Debug - Sending voice request to ${API_BASE_URL}${API_ENDPOINTS.voice}`);
        
        // Send the audio to the STT service
        let response;
        try {
            // Create FormData and append all fields directly with the audio blob
            const formData = new FormData();
            formData.append('audio_data', audioBlob, 'audio.wav'); // File upload with filename
            formData.append('model', state.currentModel || 'tinyllama:latest');
            if (state.currentMode) {
                formData.append('mode', state.currentMode);
            }
            formData.append('generate_audio', state.useVoiceResponse ? 'true' : 'false');
            formData.append('user_id', state.userId || 'web_user');
            
            console.log('Sending FormData with audio blob directly');
            response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.voice}`, {
                method: 'POST',
                // Don't set Content-Type header - browser will set it with boundary
                body: formData,
                signal: controller.signal
            });
        } catch (error) {
            console.error('Network error during voice processing:', error);
            if (error.name === 'AbortError') {
                throw new Error('Speech recognition timed out. The server took too long to process your audio.');
            } else {
                throw new Error('NetworkError');
            }
        }
        
        clearTimeout(timeoutId); // Clear the timeout if request completes
        
        if (!response.ok) {
            console.error(`STT API error: ${response.status}`, response);
            // Check specific status codes for better error messages
            if (response.status === 413) {
                throw new Error('Audio file too large for speech recognition');
            } else if (response.status === 504 || response.status === 408) {
                throw new Error('Speech recognition timed out on the server');
            } else {
                throw new Error(`STT API error: ${response.status}`);
            }
        }
        
        console.log('STT response received, parsing JSON...');
        let data;
        try {
            data = await response.json();
            console.log('STT response data:', data);
        } catch (jsonError) {
            console.error('Failed to parse STT response as JSON:', jsonError);
            throw new Error('Invalid response from speech recognition service');
        }
        
        // If we got a transcription
        if (data.text && data.text.trim()) {
            console.log('Voice recognized as:', data.text);
            // Add user message with the transcription
            addUserMessage(data.text);
            
            // Send recognized text to chat API
            await sendMessage(data.text);
        } else {
            console.warn('No text in STT response:', data);
            updateStatusMessage('Could not recognize speech');
            addSystemMessage('I couldn\'t understand what you said. Please try again or use text input.');
        }
    } catch (error) {
        console.error('Error with speech-to-text:', error);
        updateStatusMessage('Error processing speech');
        // Show a user-friendly error message
        addSystemMessage(`Sorry, there was an error processing your voice: ${error.message || 'Unknown error'}`);
    }
}

async function sendMessage(text) {
    try {
        // Show typing indicator
        showTypingIndicator();
        
        // Update status
        updateStatusMessage('AI is thinking...');
        
        // Create AbortController to handle timeouts
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
            console.log('Request timeout reached, aborting...');
            controller.abort('Request timeout');
        }, 120000); // 60-second timeout
        
        console.log(`Sending request to ${API_BASE_URL}${API_ENDPOINTS.chat}`);
        
        let response;
        try {
            // Prepare request payload with text and selected model
            const payload = {
                text: text
            };
            
            // Add model parameter if available
            if (state.currentModel && state.currentModel !== 'default') {
                payload.model = state.currentModel;
            }
            
            // Add voice response preference
            payload.generate_audio = state.useVoiceResponse;
            
            console.log('Sending chat request with payload:', payload);
            
            response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.chat}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload),
                signal: controller.signal
            });
        } catch (error) {
            console.error('Network error during fetch:', error);
            if (error.name === 'AbortError') {
                throw error; // Let the outer catch block handle abort errors
            } else {
                throw new Error('NetworkError');
            }
        }
        
        clearTimeout(timeoutId); // Clear the timeout if request completes
        
        if (!response.ok) {
            // Log detailed information about the error
            console.error(`API Error (${response.status}): ${response.statusText}`);
            let errorDetail = '';
            
            try {
                // Try to get error details from the response body if available
                const errorData = await response.text();
                console.error('Error response body:', errorData);
                try {
                    const parsed = JSON.parse(errorData);
                    errorDetail = parsed.detail || '';
                } catch (e) {
                    // Not JSON, use as is
                    errorDetail = errorData;
                }
            } catch (e) {
                console.error('Could not read error response body');
            }
            
            throw new Error(`API error: ${response.status} - ${errorDetail}`);
        }
        
        const data = await response.json();
        console.log('API response:', data);
        
        // Remove typing indicator
        hideTypingIndicator();
        
        // Add companion message
        addCompanionMessage(data.text, data.emotion);
        
        // Play audio if voice response is enabled and audio_url is available
        if (state.useVoiceResponse && data.audio_url) {
            playResponseAudio(data.audio_url);
        }
        
        updateStatusMessage('Ready');
    } catch (error) {
        hideTypingIndicator();
        console.error('Error in chat:', error);
        
        if (error.name === 'AbortError') {
            updateStatusMessage('Request timed out');
            addSystemMessage('Sorry, the AI is taking too long to respond. This might be because the LLM is busy or the request is complex. Please try again or try a shorter message.');
        } else if (error.message === 'NetworkError') {
            updateStatusMessage('Network error');
            addSystemMessage('Sorry, I couldn\'t connect to the AI service. Please check your network connection and make sure the backend services are running.');
        } else if (error.message.includes('API error: 404')) {
            updateStatusMessage('Service not found');
            addSystemMessage('Sorry, the AI service endpoint was not found. This could mean the backend API has changed or is not running.');
        } else if (error.message.includes('API error: 500')) {
            updateStatusMessage('Server error');
            addSystemMessage('The AI service encountered an internal error. This might be due to issues with the language model or text-to-speech service.');
        } else if (error.message.includes('API error: 503')) {
            updateStatusMessage('Service unavailable');
            addSystemMessage('The AI service is currently unavailable. This usually happens when one of the backend services (Ollama, TTS, or STT) is not responding.');
        } else {
            updateStatusMessage('Error getting response');
            addSystemMessage('Sorry, I encountered an error while processing your request. Please check the console for more details.');
        }
    }
}

// UI functions
function addUserMessage(text) {
    const messageHTML = `
        <div class="message user">
            <div class="avatar">
                <i class="fas fa-user"></i>
            </div>
            <div class="message-content">
                <p>${formatMessageText(text)}</p>
            </div>
        </div>
    `;
    
    elements.messageContainer.insertAdjacentHTML('beforeend', messageHTML);
    scrollToBottom();
}

function addCompanionMessage(text, emotion = 'neutral') {
    const messageHTML = `
        <div class="message companion">
            <div class="avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <p>${formatMessageText(text)}</p>
            </div>
        </div>
    `;
    
    elements.messageContainer.insertAdjacentHTML('beforeend', messageHTML);
    scrollToBottom();
    
    // Update emotion indicator
    updateEmotionIndicator(emotion);
}

function addSystemMessage(text) {
    const messageHTML = `
        <div class="system-message">
            <p>${text}</p>
        </div>
    `;
    
    elements.messageContainer.insertAdjacentHTML('beforeend', messageHTML);
    scrollToBottom();
}

function showTypingIndicator() {
    const typingHTML = `
        <div class="message companion typing" id="typing-indicator">
            <div class="avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    `;
    
    elements.messageContainer.insertAdjacentHTML('beforeend', typingHTML);
    scrollToBottom();
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function updateStatusMessage(message) {
    elements.statusIndicator.textContent = message;
}

function updateEmotionIndicator(emotion) {
    const icon = emotionIcons[emotion] || emotionIcons.neutral;
    elements.emotionIndicator.textContent = icon;
    elements.emotionIndicator.className = `emotion ${emotion}`;
}

function formatMessageText(text) {
    // Replace newlines with <br>
    text = text.replace(/\n/g, '<br>');
    
    // Simple markdown for bold and italics
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    return text;
}

function scrollToBottom() {
    elements.messageContainer.scrollTop = elements.messageContainer.scrollHeight;
}

// Audio playback
async function playResponseAudio(audioUrl) {
    try {
        updateStatusMessage('Playing audio response...');
        
        let text;
        
        // Check if we received a URL with query parameters for text-to-speech
        if (audioUrl.includes('/text-to-speech')) {
            // Extract the text from the URL if it's a query parameter
            const urlObj = new URL(audioUrl.startsWith('/') ? `${API_BASE_URL}${audioUrl}` : audioUrl);
            text = urlObj.searchParams.get('text');
            
            if (!text) {
                console.error('No text parameter found in audio URL');
                updateStatusMessage('Error retrieving audio');
                return;
            }
            
            console.log('Extracted text for TTS:', text);
            
            // Make a direct POST request to the text-to-speech endpoint
            const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.textToSpeech}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text
                })
            });
            
            if (!response.ok) {
                throw new Error(`TTS API error: ${response.status}`);
            }
            
            // Get audio blob from response
            const audioBlob = await response.blob();
            audioUrl = URL.createObjectURL(audioBlob);
            console.log('Created audio blob URL:', audioUrl);
        } else if (audioUrl.startsWith('/')) {
            // For other relative URLs, make them absolute
            audioUrl = `${API_BASE_URL}${audioUrl}`;
        }
        
        console.log('Playing audio from URL:', audioUrl);
        const audio = new Audio(audioUrl);
        
        // Set up event handlers
        audio.onerror = (e) => {
            console.error('Audio playback error:', e);
            updateStatusMessage('Error playing audio');
            addSystemMessage('Sorry, there was an error playing the audio response.');
        };
        
        audio.onended = () => {
            updateStatusMessage('Ready');
            // Clean up blob URL if we created one
            if (audioUrl.startsWith('blob:')) {
                URL.revokeObjectURL(audioUrl);
            }
        };
        
        await audio.play();
    } catch (error) {
        console.error('Error playing audio:', error);
        updateStatusMessage('Error playing audio');
        addSystemMessage('Sorry, there was an error playing the audio response. This might be due to network issues or an unsupported audio format.');
    }
}

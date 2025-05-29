import streamlit as st
import requests
import io
import tempfile
import os
import numpy as np
from PIL import Image
from streamlit_realtime_audio_recorder import audio_recorder
import base64
import hashlib
from pydub import AudioSegment

# Constants
BACKEND_URL = "http://127.0.0.1:5000/api"

# CSS Styling (keeping your existing CSS)
CHATGPT_CSS = """
<style>
html, body, .main, .block-container, .stApp {
    margin: 0 !important;
    padding: 0 !important;
    width: 100vw !important;
    min-width: 100vw !important;
    max-width: 100vw !important;
    height: 100dvh !important;
    min-height: 100dvh !important;
    max-height: 100dvh !important;
    overflow-y: auto !important;
    position: relative !important;
}
.sidebar {
    background: var(--secondary-background-color);
    padding: 1rem;
    height: 100dvh;
    overflow-y: auto;
    overflow-x: hidden !important;
    box-sizing: border-box;
}
.chat-container {
    width: 100%;
    min-width: 0;
    max-width: 100%;
    height: 100dvh !important;
    min-height: 100dvh !important;
    max-height: 100dvh !important;
    overflow-y: auto !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    position: relative;
    box-sizing: border-box;
    background: transparent !important;
}
.chat-container.centered {
    justify-content: center !important;
    align-items: center !important;
    display: flex !important;
    flex-direction: column !important;
    overflow-y: auto !important;
}
.chat-messages {
    flex: 1 1 auto;
    width: 100%;
    min-width: 0;
    max-width: 100%;
    max-height: calc(100dvh - 100px) !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-bottom: 0;
    background: transparent !important;
    box-sizing: border-box;
}
.input-container {
    background: #23242b;
    border-radius: 2.2em;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
    padding: 0.5em;
    width: 100%;
    max-width: 700px;
    margin: 0 auto;
    box-sizing: border-box;
}
.input-container.centered {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}
.input-container.bottom {
    position: sticky;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 10;
}
.input-container .stTextInput > div > input {
    background: #181a20 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 1.2em !important;
    font-size: 1.1em !important;
    padding: 0.6em 1.1em !important;
    width: 100%;
    box-sizing: border-box;
}
.buttons-row {
    display: flex;
    justify-content: flex-end;
    margin-top: 0.5em;
}
.input-container button {
    background: none;
    border: none;
    font-size: 1.4em;
    color: #bdbdbd;
    cursor: pointer;
    border-radius: 50%;
    transition: background 0.15s, color 0.15s;
    padding: 0.2em 0.4em;
}
.input-container button:hover {
    background: #33374a;
    color: #fff;
}
body::-webkit-scrollbar, html::-webkit-scrollbar, .stApp::-webkit-scrollbar {
    display: none !important;
}
/* Audio recording status styles */
.audio-recording {
    background: #ff4444 !important;
    color: white !important;
    animation: pulse 1s infinite;
}
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.7; }
    100% { opacity: 1; }
}
</style>
"""

def convert_audio_to_bytes(audio_data):
    """
    Convert audio data to WAV bytes format using pydub, handling different input types.
    FFmpeg must be installed and in the system PATH for pydub to work with non-WAV formats
    
    Args:
        audio_data: Audio data in various formats (bytes, numpy array, file-like, base64 string, or dict)
    
    Returns:
        bytes: Audio data as WAV bytes, or None if conversion fails
    """
    if audio_data is None:
        st.warning("Audio data is None, skipping conversion.")
        return None

    processed_audio_data = None

    try:
        if isinstance(audio_data, dict):
            # Try to extract audio from common dictionary keys
            if 'audio_bytes' in audio_data and isinstance(audio_data['audio_bytes'], bytes):
                processed_audio_data = audio_data['audio_bytes']
                st.info("Extracted audio from 'audio_bytes' key in dict.")
            elif 'audioData' in audio_data and isinstance(audio_data['audioData'], str):
                # Assuming base64 encoded string if it's under 'audioData'
                try:
                    processed_audio_data = base64.b64decode(audio_data['audioData'])
                except base64.binascii.Error as e:
                    st.error(f"Error decoding base64 audio data from dict: {str(e)}")
                    return None
            else:
                st.error(f"Received a dictionary but could not find 'audio_bytes' (bytes) or 'audioData' (base64 string) keys. Dict keys: {list(audio_data.keys())}")
                return None
        elif isinstance(audio_data, str):
            # Assuming base64 encoded string if it's a raw string
            try:
                processed_audio_data = base64.b64decode(audio_data)
                st.info("Decoded base64 audio from string.")
            except base64.binascii.Error as e:
                st.error(f"Error decoding base64 audio data from string: {str(e)}")
                return None
        elif isinstance(audio_data, bytes):
            processed_audio_data = audio_data
            st.info("Audio data is already bytes.")
        elif isinstance(audio_data, np.ndarray):
            # This part might need adjustment based on how audio_recorder provides numpy array data.
            # For now, let's assume it's raw audio bytes that can be put into BytesIO.
            # If it's raw PCM samples, more info (sample rate, channels, sample width) is needed
            # to construct an AudioSegment directly.
            # For simplicity, we assume it's byte data if it's a numpy array here.
            # This might be an oversimplification.
            st.warning("Received numpy array; attempting to treat as bytes. This may not be correct if it's raw PCM samples without format info.")
            processed_audio_data = audio_data.tobytes()
        elif isinstance(audio_data, io.BytesIO):
            processed_audio_data = audio_data.getvalue()
            st.info("Extracted audio from BytesIO object.")
        else:
            st.error(f"Unsupported audio_data type: {type(audio_data)}. Expected dict, str (base64), bytes, numpy.ndarray, or BytesIO.")
            return None

        if processed_audio_data is None or not isinstance(processed_audio_data, bytes) or len(processed_audio_data) == 0:
            st.error(f"Processed audio data is invalid or empty. Type: {type(processed_audio_data)}")
            return None
        
        audio_data_io = io.BytesIO(processed_audio_data)
        
        # Load audio using pydub.
        try:
            # pydub attempts to infer format. If it's raw PCM, it might fail without more info.
            # If audio_recorder provides WAV or MP3 bytes, this should work.
            audio_segment = AudioSegment.from_file(audio_data_io)
        except Exception as e: 
            st.error(f"Pydub failed to load audio. Error: {str(e)}. Ensure FFmpeg is installed and in PATH if not WAV. Input data length: {len(processed_audio_data)} bytes.")
            # For debugging, you could try to save the bytes to a file here
            # with open("debug_audio_input.raw", "wb") as f:
            #     f.write(processed_audio_data)
            # st.info("Saved problematic audio data to debug_audio_input.raw")
            return None

        # Export as WAV to a BytesIO object
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")
        return wav_io.getvalue()
        
    except Exception as e:
        st.error(f"General error in convert_audio_to_bytes: {str(e)}")
        # Log the type of audio_data that caused the issue if it's not already clear
        if not isinstance(audio_data, (dict, str, bytes, np.ndarray, io.BytesIO)):
            st.error(f"Problematic audio_data type was: {type(audio_data)}")
        return None

# Audio processing function
def process_audio_and_get_transcription(audio_data, backend_url, auth_token):
    """Processes audio data and sends it to the backend for transcription."""
    if audio_data is None:
        st.warning("No audio data received to process.")
        return None

    wav_bytes = convert_audio_to_bytes(audio_data)
    if not wav_bytes:
        st.error("Audio conversion failed, cannot transcribe.")
        return None

    st.info(f"Sending {len(wav_bytes)} bytes of WAV data for transcription.")
    files = {'file': ('audio.wav', wav_bytes, 'audio/wav')}
    headers = {"Authorization": f"Bearer {auth_token}"}
    transcribe_url = f"{backend_url}/transcribe"
    
    try:
        response = requests.post(transcribe_url, files=files, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        transcription_response = response.json()
        st.success("Transcription received successfully.")
        return transcription_response.get("transcription", "No transcription found in response.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error sending audio for transcription: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            st.error(f"Backend response: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred during transcription request: {str(e)}")
        return None

def send_message_to_ai(chat_id, message_content, headers):
    """
    Send message to AI and get response
    
    Args:
        chat_id: Current chat ID
        message_content: The message to send
        headers: Authorization headers
    
    Returns:
        tuple: (success, ai_response)
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/chats/{chat_id}/message",
            json={"content": message_content},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            ai_message = response.json().get('ai_message')
            if ai_message:
                return True, ai_message
            else:
                st.error("No AI response received. Please try again.")
                return False, None
        else:
            st.error(f"AI request failed: {response.status_code} - {response.text}")
            return False, None
            
    except requests.exceptions.Timeout:
        st.error("AI request timed out. Please try again.")
        return False, None
    except requests.exceptions.RequestException as e:
        st.error(f"Network error during AI request: {str(e)}")
        return False, None
    except Exception as e:
        st.error(f"Error getting AI response: {str(e)}")
        return False, None

def get_tts_audio(text, headers):
    """
    Get TTS audio for the given text. Returns a full URL.
    
    Args:
        text: Text to convert to speech
        headers: Authorization headers
    
    Returns:
        audio_url or None
    """
    try:
        tts_response = requests.post(
            f"{BACKEND_URL}/tts",  # BACKEND_URL is "http://127.0.0.1:5000/api"
            json={'text': text},
            headers=headers,
            timeout=15
        )
        
        if tts_response.status_code == 200:
            audio_path = tts_response.json().get('audio_url')  # e.g., "/static/audio/file.mp3"
            if audio_path:
                if audio_path.startswith("http://") or audio_path.startswith("https://"):
                    st.info(f"TTS returned full URL: {audio_path}")
                    return audio_path  # Already a full URL
                
                # Construct full URL.
                # BACKEND_URL is "http://127.0.0.1:5000/api"
                # audio_path from backend is typically like "/static/audio/file.mp3"
                # The goal is "http://127.0.0.1:5000/api/static/audio/file.mp3"
                # which matches the backend log format.
                
                base_url_for_static = BACKEND_URL # As /api/static/... is the path
                
                # Ensure audio_path starts with a slash if it's a path segment relative to BACKEND_URL
                if not audio_path.startswith("/"):
                    audio_path = "/" + audio_path
                    
                full_url = f"{base_url_for_static.rstrip('/')}{audio_path}"
                st.info(f"Constructed full TTS URL: {full_url}")
                return full_url
            st.warning("TTS service returned no audio_url.")
            return None
        else:
            st.warning(f"TTS service unavailable. Status: {tts_response.status_code}, Response: {tts_response.text}")
            return None
            
    except requests.exceptions.Timeout:
        st.warning(f"TTS request timed out for text: {text[:50]}...")
        return None
    except requests.exceptions.RequestException as e:
        st.warning(f"TTS network error: {str(e)}")
        return None
    except Exception as e:
        st.warning(f"General TTS error: {str(e)}")
        return None

def generate_audio_hash(audio_data):
    """
    Generate a hash for audio data to detect changes
    
    Args:
        audio_data: Audio data in any format
    
    Returns:
        str: MD5 hash of the audio data
    """
    try:
        # Convert to bytes first
        audio_bytes = convert_audio_to_bytes(audio_data)
        
        if audio_bytes is None or len(audio_bytes) == 0:
            return None
        
        # Generate MD5 hash
        return hashlib.md5(audio_bytes).hexdigest()
    
    except Exception as e:
        st.error(f"Error generating audio hash: {str(e)}")
        return None

# Input Bar Rendering Function
def render_input_bar():
    """
    Renders the input bar with text input, audio recorder, file upload, and send button,
    fixed at the bottom of the chat area.
    
    Returns:
        tuple: (user_text, audio_bytes, uploaded_file, send_clicked)
    """
    # Input bar is always at the bottom
    st.markdown('<div class="input-container bottom">', unsafe_allow_html=True)
    
    # Text input
    user_text = st.text_input(
        "Message",
        placeholder="Type your message or use voice recording...",
        key="user_text_input",
        label_visibility="collapsed"
    )
    
    # Buttons row
    with st.container():
        st.markdown('<div class="buttons-row">', unsafe_allow_html=True)
        col_empty, col_audio, col_upload, col_send = st.columns([4, 1, 1, 1])
        
        # Audio recorder
        with col_audio:
            # Updated audio_recorder with supported parameters
            audio_bytes = audio_recorder(
                # How often to yield audio data (in ms)
                interval=250,  
                # Silence threshold (lower means more sensitive to sound)
                threshold=40,  
                # How long to wait in silence before stopping (in ms)
                silenceTimeout=1500, 
                #key="chat_audio_recorder_input_v3" # Unique key
            )
            # The audio_recorder component provides its own visual feedback.
            # The custom st.markdown for "Audio captured!" or "Record" is removed.
        
        # File upload
        with col_upload:
            uploaded_file = st.file_uploader(
                "📎",
                type=["pdf", "png", "jpg", "jpeg", "wav", "mp3"],
                key="file_uploader_widget",
                label_visibility="collapsed"
            )
        
        # Send button
        with col_send:
            send_clicked = st.button("➤", key="send_button", help="Send message")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    return user_text, audio_bytes, uploaded_file, send_clicked

# Main Render Function
def render(auth_token=None):
    """
    Renders the chat page with sidebar, chat messages, and input bar.
    
    Args:
        auth_token (str, optional): Authentication token for API requests.
    """
    st.markdown(CHATGPT_CSS, unsafe_allow_html=True)
    

    if auth_token:
        st.session_state.auth_token = auth_token

    headers = {"Authorization": f"Bearer {st.session_state.get('auth_token', '')}"}
    
    # Chat naming automation function
    def maybe_generate_chat_title(chat_id, user_message, headers):
        try:
            chat_url = f"{BACKEND_URL}/chats/{chat_id}"
            chat_res = requests.get(chat_url, headers=headers)
            if chat_res.ok:
                chat = chat_res.json()
                if chat.get('title', '').lower() in ("untitled", "new chat", "", None):
                    title_res = requests.post(
                        f"{BACKEND_URL}/chats/{chat_id}/title", 
                        json={"user_message": user_message}, 
                        headers=headers
                    )
        except Exception as e:
            # Silent fail for title generation
            pass

    # Initialize session state
    if 'selected_chat_id' not in st.session_state:
        st.session_state.selected_chat_id = None
    if 'last_audio_hash' not in st.session_state:
        st.session_state.last_audio_hash = None
    if 'recording_active' not in st.session_state:
        st.session_state.recording_active = False

    def ensure_chat_exists():
        """Ensure a chat exists, create one if needed"""
        if not st.session_state.selected_chat_id:
            try:
                res = requests.post(f"{BACKEND_URL}/chats", headers=headers)
                if res.status_code == 200:
                    st.session_state.selected_chat_id = res.json()['id']
                    return True
                else:
                    st.error("Failed to create new chat")
                    return False
            except Exception as e:
                st.error(f"Error creating chat: {str(e)}")
                return False
        return True

    # Sidebar for chat management
    with st.sidebar:
        st.markdown("## Chats")
        if st.button("+ New Chat", key="new_chat_button"):
            try:
                res = requests.post(f"{BACKEND_URL}/chats", headers=headers)
                if res.status_code == 200:
                    st.session_state.selected_chat_id = res.json()['id']
                    st.rerun()
                else:
                    st.error("Failed to create new chat")
            except Exception as e:
                st.error(f"Error creating chat: {str(e)}")
        
        # Load and display existing chats
        try:
            chats_response = requests.get(f"{BACKEND_URL}/chats", headers=headers)
            if chats_response.status_code == 200:
                chats = chats_response.json()
                for i, chat in enumerate(chats):
                    if st.button(
                        chat['title'], 
                        key=f"chat_button_{chat['id']}_{i}",
                        use_container_width=True
                    ):
                        st.session_state.selected_chat_id = chat['id']
                        st.rerun()
            else:
                st.error(f"Failed to load chats. Status: {chats_response.status_code}")
        except Exception as e:
            st.error(f"Error loading chats: {str(e)}")

    # Load chat messages
    messages = []
    if st.session_state.selected_chat_id:
        try:
            res = requests.get(f"{BACKEND_URL}/chats/{st.session_state.selected_chat_id}", headers=headers)
            if res.status_code == 200:
                messages = res.json().get('messages', [])
            else:
                st.error("Failed to load chat messages")
        except Exception as e:
            st.error(f"Error loading messages: {str(e)}")

    # Chat container setup
    # If no chat is selected, center the content (initial welcome/prompt to select/create chat).
    # If a chat is selected (even if it's new and has no messages yet), align to top.
    is_centered_content = st.session_state.selected_chat_id is None # This refers to chat content, not input bar
    container_class = "chat-container centered" if is_centered_content else "chat-container"
    
    with st.container():
        st.markdown(f'<div class="{container_class}" id="chat-container">', unsafe_allow_html=True)
        st.markdown('<div class="chat-messages" id="chat-messages">', unsafe_allow_html=True)
        
        # Display chat messages
        if messages:
            for msg_idx, msg in enumerate(messages):
                with st.chat_message(msg['sender']):
                    st.write(msg['content'])
                    # Add TTS for AI messages
                    if msg['sender'] == 'ai':
                        audio_url = get_tts_audio(msg['content'], headers)
                        if audio_url:
                            st.info(f"Historical loop - URL for st.audio: {audio_url}")
                            with st.container(): # Wrap st.audio in a container
                                st.audio(audio_url)
        else:
            st.markdown("### 👋 Welcome! Start a new chat or send a message to begin.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Render input bar - it will now always be at the bottom
        user_text, audio_bytes, uploaded_file, send_clicked = render_input_bar()
        
        # Handle audio input
        if audio_bytes is not None and len(audio_bytes) > 0:
            # Generate hash to detect new audio
            audio_hash = generate_audio_hash(audio_bytes)
            
            if audio_hash and audio_hash != st.session_state.get('last_audio_hash'):
                st.session_state.last_audio_hash = audio_hash
                st.session_state.recording_active = True # Potentially manage this state more carefully
                
                if ensure_chat_exists():
                    with st.spinner("Processing audio..."):
                        transcribed_text = process_audio_and_get_transcription(
                            audio_bytes, 
                            BACKEND_URL, # Assuming BACKEND_URL is defined globally
                            st.session_state.auth_token
                        )
                        
                        if transcribed_text: # Check if transcription was successful
                            # Display user message
                            with st.chat_message("user"):
                                st.write(transcribed_text)
                            
                            # Get AI response
                            ai_success, ai_response = send_message_to_ai(
                                st.session_state.selected_chat_id, 
                                transcribed_text, 
                                headers
                            )
                            
                            if ai_success and ai_response:
                                # Display AI response
                                with st.chat_message("ai"):
                                    st.write(ai_response)
                                    # Add TTS
                                    audio_url = get_tts_audio(ai_response, headers)
                                    if audio_url:
                                        st.info(f"New AI msg (audio input) - URL for st.audio: {audio_url}")
                                        with st.container(): # Wrap st.audio in a container
                                            st.audio(audio_url)
                                
                                # Generate chat title if needed
                                maybe_generate_chat_title(
                                    st.session_state.selected_chat_id, 
                                    transcribed_text, 
                                    headers
                                )
                        else:
                            st.warning("Audio processed, but no transcription was returned.")
                        
                        st.session_state.recording_active = False # Reset recording state
                        st.rerun()
        
        # Handle file upload
        if uploaded_file is not None:
            if ensure_chat_exists():
                try:
                    files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    res = requests.post(f"{BACKEND_URL}/utils/extract", files=files, headers=headers)
                    
                    if res.status_code == 200:
                        content = res.json().get('text', '')
                        if content:
                            # Display user message
                            with st.chat_message("user"):
                                st.write(f"*Uploaded file: {uploaded_file.name}*")
                                st.write(content)
                            
                            # Get AI response
                            ai_success, ai_response = send_message_to_ai(
                                st.session_state.selected_chat_id, 
                                content, 
                                headers
                            )
                            
                            if ai_success and ai_response:
                                with st.chat_message("ai"): # Changed "assistant" to "ai"
                                    st.write(ai_response)
                                    # Add TTS
                                    audio_url = get_tts_audio(ai_response, headers)
                                    if audio_url:
                                        st.audio(audio_url)
                            
                            st.rerun()
                    else:
                        st.error(f"File processing failed: {res.status_code}")
                        
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
        
        # Handle text message send
        if send_clicked and user_text.strip():
            if ensure_chat_exists():
                content = user_text.strip()
                
                # Display user message
                with st.chat_message("user"):
                    st.write(content)
                
                # Get AI response
                ai_success, ai_response = send_message_to_ai(
                    st.session_state.selected_chat_id, 
                    content, 
                    headers
                )
                
                if ai_success and ai_response:
                    with st.chat_message("ai"):
                        st.write(ai_response)
                        # Add TTS
                        audio_url = get_tts_audio(ai_response, headers)
                        if audio_url:
                            st.info(f"New AI msg (text input) - URL for st.audio: {audio_url}")
                            with st.container(): # Wrap st.audio in a container
                                st.audio(audio_url)
                    
                    # Generate chat title if needed
                    maybe_generate_chat_title(
                        st.session_state.selected_chat_id, 
                        content, 
                        headers
                    )
                
                # Clear the text input by rerunning
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
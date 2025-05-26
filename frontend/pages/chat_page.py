import streamlit as st
import requests
from datetime import datetime
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import speech_recognition as sr
import av
import io

BACKEND_URL = "http://127.0.0.1:5000/api"

CHATGPT_CSS = """
<style>
/* Main layout */
.main {
    display: flex;
    height: 100vh;
}
/* Sidebar */
.sidebar {
    background: #202123;
    width: 260px;
    padding: 0.5rem;
    display: flex;
    flex-direction: column;
    height: 100vh;
}
/* Chat container */
.chat-container {
    flex-grow: 1;
    background: #343541;
    height: calc(100vh - 160px);
    overflow-y: auto;
    padding: 2rem 0;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}
/* Messages */
.chat-message {
    display: flex;
    padding: 1.5rem;
    gap: 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}
.message {
    color: #ececf1;
    font-size: 1rem;
    line-height: 1.5;
    max-width: 48rem;
    margin: 0 auto;
    display: flex;
    gap: 1rem;
    padding: 0 1rem;
}
/* Input area */
.input-container {
    position: sticky;
    bottom: 0;
    left: 260px;
    right: 0;
    padding: 1.5rem 1rem;
    background: #343541;
}
.input-box {
    max-width: 48rem;
    margin: 0 auto;
    background: #40414f;
    border-radius: 0.75rem;
    border: 1px solid rgba(255,255,255,0.1);
    padding: 0.75rem;
    display: flex;
    gap: 0.5rem;
}
/* Buttons */
.new-chat-btn {
    width: 100%;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 0.375rem;
    padding: 0.75rem;
    color: #ececf1;
    margin-bottom: 1rem;
}
/* Chat history */
.chat-history {
    overflow-y: auto;
    flex-grow: 1;
}
.chat-history-item {
    padding: 0.75rem;
    border-radius: 0.375rem;
    color: #ececf1;
    cursor: pointer;
    margin: 0.25rem 0;
}
/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: #666;
    border-radius: 3px;
}
</style>
"""

class SpeechToTextProcessor(AudioProcessorBase):
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.audio_data = b""

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        self.audio_data += frame.to_ndarray().tobytes()
        return frame

    def get_text(self):
        if not self.audio_data:
            return ""
        try:
            audio_file = io.BytesIO(self.audio_data)
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
            return text
        except Exception as e:
            return f"Error: {e}"

# Helper: Translate text to English using backend
def translate_to_english(text, headers):
    resp = requests.post(f"{BACKEND_URL}/utils/translate", json={"text": text}, headers=headers)
    if resp.status_code == 200:
        return resp.json().get("translated", text)
    return text

# Helper: Extract text from file using backend
def extract_text_from_file(file, headers):
    files = {"file": file}
    resp = requests.post(f"{BACKEND_URL}/api/utils/extract", files=files, headers=headers)
    if resp.status_code == 200:
        return resp.json().get("text", "")
    return ""

# Helper: Get OpenAI response from backend
def get_openai_response(prompt, headers):
    resp = requests.post(f"{BACKEND_URL}/openai", json={"prompt": prompt}, headers=headers)
    if resp.status_code == 200:
        return resp.json().get("response", "")
    return ""

# Helper: Send message to Infermedica
def get_infermedica_response(chat_id, content, headers):
    resp = requests.post(f"{BACKEND_URL}/chats/{chat_id}/message", json={"content": content}, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        return data.get("ai_message", ""), data
    return "", {}

# Helper: Generate image using backend
def generate_image(prompt, headers):
    resp = requests.post(f"{BACKEND_URL}/generate_image", json={"prompt": prompt}, headers=headers)
    if resp.status_code == 200:
        return resp.json().get("image_url", None)
    return None

# Helper: Get TTS audio from backend
def get_tts_audio(text, headers):
    resp = requests.post(f"{BACKEND_URL}/tts", json={"text": text}, headers=headers)
    if resp.status_code == 200:
        return resp.json().get("audio_url", None)
    return None

def render(on_start_diagnosis=lambda: set_page('wizard'), backend_url=BACKEND_URL, auth_token=st.session_state.get('auth_token', None)):
    st.markdown(CHATGPT_CSS, unsafe_allow_html=True)
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    } if auth_token else {}

    # Initialize session state
    if 'selected_chat_id' not in st.session_state:
        st.session_state.selected_chat_id = None
    if 'voice_text' not in st.session_state:
        st.session_state.voice_text = ""

    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div class="sidebar">
            <button class="new-chat-btn">+ New Chat</button>
            <div class="chat-history">
        """, unsafe_allow_html=True)
        
        if st.button("+ New Chat", key="new_chat"):
            try:
                resp = requests.post(
                    f"{backend_url}/chats",
                    headers=headers  # <-- Only headers, no json body!
                )
                if resp.status_code == 200:
                    st.session_state.selected_chat_id = resp.json().get('id')
                    st.rerun()
                else:
                    st.error(f"Failed to create new chat: ({resp.status_code}) {resp.text}")
            except Exception as e:
                st.error(f"Error: {e}")

        try:
            chats = requests.get(f"{backend_url}/chats", headers=headers).json()
            # If the backend returns an error as a dict or a string, handle it
            if isinstance(chats, dict) and chats.get("error"):
                st.error(f"Backend error: {chats['error']}")
                chats = []
            elif not isinstance(chats, list):
                st.error(f"Unexpected response from backend: {chats}")
                chats = []
        except Exception:
            st.error("Failed to fetch chats")
            chats = []

        for chat in sorted(chats, key=lambda c: c.get("created_at", ""), reverse=True):
            title = chat.get('title', 'New Chat')
            date = datetime.fromisoformat(chat['created_at']).strftime('%b %d') if chat.get('created_at') else ""
            if st.button(f"{title}\n{date}", key=f"chat_{chat.get('id')}"):
                st.session_state.selected_chat_id = chat.get('id')
                st.rerun()

        st.markdown("</div></div>", unsafe_allow_html=True)

    # Main chat area
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    if st.session_state.selected_chat_id:
        try:
            chat_resp = requests.get(
                f"{backend_url}/chats/{st.session_state.selected_chat_id}",
                headers=headers
            )
            chat = chat_resp.json()
            if isinstance(chat, dict) and chat.get("messages"):
                for msg in chat["messages"]:
                    avatar = "🧑" if msg.get("sender") == "user" else "🤖"
                    st.markdown(f"""
                    <div class="chat-message">
                        <div class="message">
                            <div class="avatar">{avatar}</div>
                            <div>{msg.get("content", "")}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    # If this is an AI message, add TTS play button
                    if msg.get("sender") == "ai" and msg.get("content"):
                        if st.button(f"🔊 Play AI Voice {msg['created_at']}", key=f"tts_{msg['created_at']}"):
                            audio_url = get_tts_audio(msg["content"], headers)
                            if audio_url:
                                st.audio(audio_url)
                            else:
                                st.error("Failed to generate voice output.")
            # Show generated images if any
            if "generated_images" in st.session_state:
                for img_url in st.session_state.generated_images:
                    st.image(img_url, caption="Generated Image", use_column_width=True)
        except Exception as e:
            st.error(f"Failed to load chat: {e}")
    else:
        st.markdown("""
        <div style="text-align: center; margin-top: 20%; color: #666;">
            <h2>Select a chat or create a new one</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Input area
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    input_col, button_col = st.columns([6, 1])
    
    with input_col:
        user_input = st.text_input(
            "Message HealthAssist...",
            key="user_input",
            label_visibility="collapsed"
        )

    with button_col:
        if st.button("Send"):
            if st.session_state.user_input.strip():
                handle_user_message(st.session_state.user_input, headers)
                st.rerun()

    file_col, voice_col = st.columns([1, 1])
    with file_col:
        uploaded_file = st.file_uploader(
            "Upload",
            type=["jpg", "png", "pdf", "wav", "mp3"],
            label_visibility="collapsed"
        )
        if uploaded_file:
            if uploaded_file.type in ["audio/wav", "audio/x-wav", "audio/mp3", "audio/mpeg"] or uploaded_file.name.lower().endswith((".wav", ".mp3")):
                files = {'file': uploaded_file}
                response = requests.post(f"{BACKEND_URL}/api/utils/extract", files=files)
                if response.status_code == 200:
                    text = response.json().get("text", "")
                    if text:
                        handle_user_message(text, headers)
                        st.rerun()
                    else:
                        st.error("No text could be extracted from the audio file.")
                else:
                    st.error(f"Failed to extract text from audio file: ({response.status_code}) {response.text}")
            else:
                files = {'file': uploaded_file}
                response = requests.post(f"{BACKEND_URL}/api/utils/extract", files=files)
                if response.status_code == 200:
                    text = response.json().get("text", "")
                    if text:
                        handle_user_message(text, headers)
                        st.rerun()
                    else:
                        st.error("No text could be extracted from the file.")
                else:
                    st.error(f"Failed to extract text from file: ({response.status_code}) {response.text}")

    with voice_col:
        ctx = webrtc_streamer(
            key="speech",
            audio_receiver_size=1024,
            async_processing=True,
            audio_processor_factory=SpeechToTextProcessor,
            video=False,  # Only audio, disables camera
        )
        if ctx and ctx.state.playing:
            st.info("Recording... Speak now!")
        if ctx and ctx.audio_processor:
            text = ctx.audio_processor.get_text()
            if text:
                if st.button("Send Voice Input"):
                    handle_user_message(text, headers)
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# New: Unified message handler for text

def handle_user_message(content, headers):
    if not st.session_state.selected_chat_id:
        st.error("No chat selected")
        return
    # Detect image generation prompt
    if any(kw in content.lower() for kw in ["generate an image", "create an image", "draw an image", "make an image"]):
        image_url = generate_image(content, headers)
        if image_url:
            if "generated_images" not in st.session_state:
                st.session_state.generated_images = []
            st.session_state.generated_images.append(image_url)
            st.success("Image generated!")
        else:
            st.error("Failed to generate image.")
        return
    # 1. Translate if not English
    lang = requests.post(f"{BACKEND_URL}/utils/detect_language", json={"text": content}, headers=headers)
    if lang.status_code == 200 and lang.json().get("lang") != "en":
        content = translate_to_english(content, headers)
    # 2. Try Infermedica
    ai_message, data = get_infermedica_response(st.session_state.selected_chat_id, content, headers)
    if not ai_message or "not configured" in ai_message.lower() or "couldn't identify" in ai_message.lower():
        # 3. Fallback to OpenAI
        ai_message = get_openai_response(content, headers)
        requests.post(f"{BACKEND_URL}/chats/{st.session_state.selected_chat_id}/message", json={"content": ai_message, "sender": "ai"}, headers=headers)
    # Store last AI message for TTS
    st.session_state.last_ai_message = ai_message

# New: Unified message handler for files

def handle_file_message(file, headers):
    if not st.session_state.selected_chat_id:
        st.error("No chat selected")
        return
    # 1. Extract text from file
    text = extract_text_from_file(file, headers)
    if not text:
        st.error("Could not extract text from file.")
        return
    # 2. Process as text
    handle_user_message(text, headers)
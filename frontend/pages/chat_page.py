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
def get_infermedica_response(chat_id, content, headers, return_followup=False, answers_dict=None):
    chat_resp = requests.get(f"{BACKEND_URL}/chats/{chat_id}", headers=headers)
    context = []
    if chat_resp.status_code == 200:
        chat_data = chat_resp.json()
        if isinstance(chat_data, dict) and chat_data.get("messages"):
            context = [m["content"] for m in chat_data["messages"] if m["sender"] in ("user", "ai")][-10:]
    payload = {"content": content, "context": context}
    if answers_dict:
        payload["answers"] = answers_dict
    resp = requests.post(f"{BACKEND_URL}/chats/{chat_id}/message", json=payload, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        if return_followup:
            return data.get("ai_message", ""), data.get("hidden", False), data.get("raw_message", ""), data.get("followup", None)
        return data.get("ai_message", ""), data.get("hidden", False), data.get("raw_message", "")
    if return_followup:
        return "", False, "", None
    return "", False, ""

# Helper: Generate image using backend
def generate_image(prompt, headers):
    resp = requests.post(f"{BACKEND_URL}/generate_image", json={"prompt": prompt}, headers=headers)
    if resp.status_code == 200:
        return resp.json().get("image_url", None)
    return None

# Helper: Get TTS audio from backend
def get_tts_audio(text, headers):
    try:
        resp = requests.post(
            f"{BACKEND_URL}/tts",
            json={"text": text},
            headers=headers
        )
        if resp.status_code == 200:
            return resp.json().get("audio_url", None)
        else:
            st.error(f"Failed to generate audio: {resp.text}")
            return None
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")
        return None

def render(on_start_diagnosis=None, backend_url=BACKEND_URL, auth_token=st.session_state.get('auth_token', None)):
    st.markdown(CHATGPT_CSS, unsafe_allow_html=True)
    
    # Check if user is authenticated
    if not auth_token:
        st.error("Please log in to use the chat.")
        return
        
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

    # Initialize session state
    if 'selected_chat_id' not in st.session_state:
        st.session_state.selected_chat_id = None
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""
    if 'should_clear_input' not in st.session_state:
        st.session_state.should_clear_input = False
    if 'conversation_context' not in st.session_state:
        st.session_state.conversation_context = []
    if 'answered_questions' not in st.session_state:
        st.session_state.answered_questions = {}

    # Clear input if needed
    if st.session_state.should_clear_input:
        st.session_state.user_input = ""
        st.session_state.should_clear_input = False

    # Sidebar with chat history
    with st.sidebar:
        st.markdown("""
        <div class="sidebar">
            <div class="chat-history">
        """, unsafe_allow_html=True)
        
        if st.button("+ New Chat", key="new_chat"):
            try:
                resp = requests.post(
                    f"{backend_url}/chats",
                    headers=headers
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
            date = datetime.fromisoformat(chat['created_at']).strftime('%b %d') if chat.get("created_at") else ""
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
                st.session_state.should_clear_input = True
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# New: Unified message handler for text

def handle_user_message(content, headers, answers_dict=None, callback=None):
    if not st.session_state.selected_chat_id:
        st.error("No chat selected")
        return
    
    # Display user message immediately
    st.markdown(f"""
    <div class="chat-message">
        <div class="message">
            <div class="avatar">🧑</div>
            <div>{content}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add context to the payload
    payload = {
        "content": content,
        "answers": answers_dict,
        "callback": callback,
        "context": st.session_state.conversation_context,
        "answered_questions": list(st.session_state.answered_questions.keys())
    }
    
    try:
        # Ensure headers are properly set
        if not headers.get("Authorization"):
            st.error("Authentication token missing. Please log in again.")
            return
            
        resp = requests.post(
            f"{BACKEND_URL}/chats/{st.session_state.selected_chat_id}/message",
            json=payload,
            headers=headers
        )
        
        if resp.status_code == 200:
            data = resp.json()
            ai_message = data.get("ai_message", "")
            
            # Display AI message
            if ai_message:
                st.markdown(f"""
                <div class="chat-message">
                    <div class="message">
                        <div class="avatar">🤖</div>
                        <div>{ai_message}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Add TTS button for AI message
                if st.button(f"🔊 Play AI Voice", key=f"tts_{datetime.now().isoformat()}"):
                    audio_url = get_tts_audio(ai_message, headers)
                    if audio_url:
                        try:
                            st.audio(audio_url, format="audio/mp3")
                        except Exception as e:
                            st.error(f"Error playing audio: {str(e)}")
            
            # Update conversation context
            st.session_state.conversation_context.append(content)
            st.session_state.conversation_context.append(ai_message)
            # Keep only last 10 messages
            st.session_state.conversation_context = st.session_state.conversation_context[-10:]
            
            st.session_state.should_clear_input = True
            st.rerun()
        elif resp.status_code == 403:
            st.error("Authentication failed. Please log in again.")
            # Clear the auth token to force re-login
            st.session_state.auth_token = None
            st.rerun()
        else:
            st.error(f"Failed to send message: {resp.text}")
    except Exception as e:
        st.error(f"Error sending message: {str(e)}")
        st.error("Full error details:", exc_info=True)

def handle_followup_submission(answers_dict, headers):
    if not st.session_state.selected_chat_id:
        st.error("No chat selected")
        return
        
    # Map frontend answers to Infermedica choice_ids
    mapped_answers = {}
    for key, value in answers_dict.items():
        if isinstance(value, str):
            if value.lower() == "yes":
                mapped_answers[key] = "present"
            elif value.lower() == "no":
                mapped_answers[key] = "absent"
            elif value.lower() == "don't know":
                mapped_answers[key] = "unknown"
            else:
                mapped_answers[key] = value
        elif isinstance(value, list):
            mapped_answers[key] = [v.lower() for v in value]
        else:
            mapped_answers[key] = value
    
    callback = st.session_state.current_callback
    handle_user_message("", headers, answers_dict=mapped_answers, callback=callback)
    st.session_state.last_followup = None
    st.session_state.current_callback = None
    st.session_state.should_clear_input = True
    st.rerun()

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
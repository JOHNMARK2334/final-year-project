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
    resp = requests.post(f"{BACKEND_URL}/tts", json={"text": text}, headers=headers)
    if resp.status_code == 200:
        return resp.json().get("audio_url", None)
    return None

def render(on_start_diagnosis=None, backend_url=BACKEND_URL, auth_token=st.session_state.get('auth_token', None)):
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
    if 'last_followup_question' not in st.session_state:
        st.session_state.last_followup_question = None
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""
    if 'should_clear_input' not in st.session_state:
        st.session_state.should_clear_input = False
    if 'last_followup' not in st.session_state:
        st.session_state.last_followup = None
    if 'last_followup_time' not in st.session_state:
        st.session_state.last_followup_time = None
    if 'current_callback' not in st.session_state:
        st.session_state.current_callback = None
    if 'answered_questions' not in st.session_state:
        st.session_state.answered_questions = {}
    if 'conversation_context' not in st.session_state:
        st.session_state.conversation_context = []
    if 'current_question_id' not in st.session_state:
        st.session_state.current_question_id = None

    # Clear input if needed
    if st.session_state.should_clear_input:
        st.session_state.user_input = ""
        st.session_state.should_clear_input = False

    # Sidebar with chat history only
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

    last_ai_message = None
    last_ai_time = None
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
                    # Track last AI message for follow-up
                    if msg.get("sender") == "ai" and msg.get("content"):
                        last_ai_message = msg.get("content")
                        last_ai_time = msg.get("created_at")
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

    # --- Highlight and handle follow-up question as a form ---
    if last_ai_message and (last_ai_message.strip().endswith('?') or (st.session_state.last_followup_question and st.session_state.last_followup_time == last_ai_time)):
        st.markdown(f"<div style='background:#fbbf24;padding:1rem;border-radius:8px;color:#222;font-weight:bold;'>🤖 {last_ai_message}</div>", unsafe_allow_html=True)
        with st.form(key="followup_form"):
            followup_answer = st.text_input("Your answer:", key="followup_input")
            submitted = st.form_submit_button("Submit")
            if submitted and followup_answer.strip():
                handle_user_message(followup_answer, headers)
                st.session_state.last_followup_question = None
                st.session_state.last_followup_time = None
                st.rerun()
        # Store the last follow-up question and its time in session state
        st.session_state.last_followup_question = last_ai_message
        st.session_state.last_followup_time = last_ai_time
    else:
        st.session_state.last_followup_question = None
        st.session_state.last_followup_time = None

    # --- Advanced follow-up UI (always shown if present) ---
    followup = getattr(st.session_state, 'last_followup', None)
    if followup:
        # Generate a unique ID for this question
        question_id = followup.get('id', followup.get('text', ''))
        
        # Check if this question has already been answered
        if question_id in st.session_state.answered_questions:
            # Skip this question as it's already been answered
            st.session_state.last_followup = None
            st.rerun()
            return

        st.markdown(
            f"""
            <div style='background:#fffbe6;border:2px solid #fbbf24;padding:1.5rem 1rem;border-radius:10px;margin:1rem 0;box-shadow:0 2px 8px #fbbf2440;'>
                <span style='font-size:1.2rem;font-weight:bold;color:#b45309;'>🤖 Follow-up:</span>
                <div style='margin-top:0.5rem;font-size:1.1rem;color:#222;'>{followup['text']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Create a form for the follow-up question
        with st.form(key=f"followup_form_{question_id}"):
            # For group questions
            answers = []
            answers_dict = {}
            valid = True
            
            # Get the items from the follow-up question
            items = followup.get('items', [])
            if not items and followup.get('text'):
                # If no items but we have text, create a single item
                items = [{
                    "text": followup['text'],
                    "type": "single",
                    "choices": ["Yes", "No", "Don't know"]
                }]
            
            for idx, item in enumerate(items):
                input_type = item.get('type', 'single')
                label = item.get('text', f"Question {idx+1}")
                choices = item.get('choices', ["Yes", "No", "Don't know"])
                
                if input_type == 'single':
                    answer = st.radio(label, choices, key=f"followup_choice_{idx}")
                elif input_type == 'multi':
                    answer = st.multiselect(label, choices, key=f"followup_multi_{idx}")
                elif input_type == 'number':
                    answer = st.number_input(label, key=f"followup_num_{idx}")
                elif input_type == 'date':
                    answer = st.date_input(label, key=f"followup_date_{idx}")
                else:
                    answer = st.text_input(label, key=f"followup_text_{idx}")
                
                if (input_type == 'multi' and not answer) or (input_type != 'multi' and not answer):
                    valid = False
                answers.append(answer)
                answers_dict[label] = answer
            
            submitted = st.form_submit_button("Submit")
            if submitted:
                if not valid:
                    st.warning("Please answer all follow-up questions before submitting.")
                else:
                    # Store the question and its answers
                    st.session_state.answered_questions[question_id] = {
                        'question': followup['text'],
                        'answers': answers_dict,
                        'timestamp': datetime.now().isoformat()
                    }
                    # Add to conversation context
                    st.session_state.conversation_context.append({
                        'question_id': question_id,
                        'question': followup['text'],
                        'answers': answers_dict
                    })
                    handle_user_message("; ".join([str(a) for a in answers]), headers, answers_dict=answers_dict)
                    st.session_state.last_followup = None
                    st.session_state.should_clear_input = True
                    st.rerun()
    else:
        # Only show the text input if there is no follow-up
        if not st.session_state.last_followup:
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
            #video=False,  # Only audio, disables camera
        )
        if ctx and ctx.state.playing:
            st.info("Recording... Speak now!")
        if ctx and ctx.audio_processor:
            text = ctx.audio_processor.get_text()
            if text:
                if st.button("Send Voice Input"):
                    handle_user_message(text, headers)
                    st.rerun()

# New: Unified message handler for text

def handle_user_message(content, headers, answers_dict=None, callback=None):
    if not st.session_state.selected_chat_id:
        st.error("No chat selected")
        return

    # Add context to the payload
    payload = {
        "content": content,
        "answers": answers_dict,
        "callback": callback,
        "context": st.session_state.conversation_context,
        "answered_questions": list(st.session_state.answered_questions.keys())
    }
    
    resp = requests.post(
        f"{BACKEND_URL}/chats/{st.session_state.selected_chat_id}/message",
        json=payload,
        headers=headers
    )
    
    if resp.status_code == 200:
        data = resp.json()
        ai_message = data.get("ai_message", "")
        hidden = data.get("hidden", False)
        followup = data.get("followup")
        callback = data.get("callback")
        
        # Check if this is a new question
        if followup:
            question_id = followup.get("id")
            if question_id in st.session_state.answered_questions:
                # Skip this question as it's already been answered
                followup = None
            else:
                # Store the question ID in answered questions
                st.session_state.answered_questions[question_id] = {
                    "question": followup["text"],
                    "timestamp": datetime.now().isoformat()
                }
        
        # Store followup and callback in session state
        st.session_state.last_followup = followup
        st.session_state.current_callback = callback
        
        if not hidden and ai_message:
            # Display the AI message
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
                    st.audio(audio_url)
                else:
                    st.error("Failed to generate voice output.")
        
        # If followup, do not show input box, let the followup form handle it
        if followup:
            return
            
        if not ai_message or "not configured" in ai_message.lower() or "couldn't identify" in ai_message.lower():
            ai_message = get_openai_response(content, headers)
            requests.post(
                f"{BACKEND_URL}/chats/{st.session_state.selected_chat_id}/message",
                json={"content": ai_message, "sender": "ai", "callback": callback},
                headers=headers
            )
            # Display the fallback message
            st.markdown(f"""
            <div class="chat-message">
                <div class="message">
                    <div class="avatar">🤖</div>
                    <div>{ai_message}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.session_state.should_clear_input = True
        st.rerun()
    else:
        st.error(f"Failed to send message: {resp.text}")

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
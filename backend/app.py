from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

from flask import Flask, request, jsonify, send_from_directory
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate
from flask_cors import CORS
from functools import wraps
from models import db, Chat, ChatMessage, User
from infermedica_conversation import infermedica_conversational_flow
from werkzeug.security import generate_password_hash, check_password_hash
from utils import detect_language, translate_to_english, extract_text_from_pdf
from openai_client import get_openai_response
import datetime
import logging
import tempfile
import uuid
from gtts import gTTS

app = Flask(__name__)
CORS(app)

# Database and JWT configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://super_user:jm32@localhost:5432/medical_assistant1')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'jwt_secret')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=1)
app.config["JWT_IDENTITY_CLAIM"] = "sub"

logging.basicConfig(level=logging.INFO)

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

print("INFERMEDICA_APP_ID:", os.getenv("INFERMEDICA_APP_ID"))
print("INFERMEDICA_APP_KEY:", os.getenv("INFERMEDICA_APP_KEY"))
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))

# --- User Registration Endpoint ---
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    if not username or not password or not email:
        return jsonify({"error": "Username, password, and email required"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    user = User(username=username, email=email, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered"}), 201

# --- User Login Endpoint ---
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "access_token": access_token,
            "user_id": user.id,
            "username": user.username
        })
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# --- Modified JWT-Protected Endpoints ---
def jwt_identity_to_int(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            user_id = int(get_jwt_identity())
            return f(user_id=user_id, *args, **kwargs)
        except ValueError:
            return jsonify({"error": "Invalid user ID format"}), 401
    return decorated_function

# --- New Chat Endpoint ---
@app.route('/api/chats', methods=['POST'])
@jwt_required()
@jwt_identity_to_int
def start_chat(user_id):
    chat = Chat(user_id=user_id, state={}, title="Untitled")
    db.session.add(chat)
    db.session.commit()
    return jsonify({
        "id": chat.id, 
        "title": chat.title, 
        "created_at": chat.created_at.isoformat()
    })

# --- List Chats Endpoint ---
@app.route('/api/chats', methods=['GET'])
@jwt_required()
@jwt_identity_to_int
def list_chats(user_id):
    chats = Chat.query.filter_by(user_id=user_id).order_by(Chat.updated_at.desc()).all()
    return jsonify([
        {
            "id": chat.id,
            "title": chat.title or f"Chat {chat.id}",
            "created_at": chat.created_at.isoformat(),
            "updated_at": chat.updated_at.isoformat()
        }
        for chat in chats
    ])

# --- Get Chat (with messages) Endpoint ---
@app.route('/api/chats/<int:chat_id>', methods=['GET'])
@jwt_required()
@jwt_identity_to_int
def get_chat(user_id, chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if chat.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403
    messages = [
        {
            "sender": m.sender,
            "content": m.content,
            "created_at": m.created_at.isoformat()
        }
        for m in sorted(chat.messages, key=lambda m: m.created_at)
    ]
    return jsonify({
        "id": chat.id,
        "title": chat.title,
        "messages": messages,
        "state": chat.state
    })

# --- Patch Chat Title Endpoint ---
@app.route('/api/chats/<int:chat_id>', methods=['PATCH'])
@jwt_required()
@jwt_identity_to_int
def patch_chat(user_id, chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if chat.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    if "title" in data:
        chat.title = data["title"]
        chat.updated_at = datetime.datetime.utcnow()
        db.session.commit()
    return jsonify({"id": chat.id, "title": chat.title})

# --- Send Message Endpoint ---
@app.route('/api/chats/<int:chat_id>/message', methods=['POST'])
@jwt_required()
@jwt_identity_to_int
def chat_message(user_id, chat_id):
    data = request.get_json()
    user_message = data.get("content")
    answers_dict = data.get("answers")
    callback = data.get("callback")  # New: Support for callback function name
    chat = Chat.query.get_or_404(chat_id)
    if chat.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    # Save user message
    msg = ChatMessage(chat_id=chat.id, sender="user", content=user_message)
    db.session.add(msg)
    db.session.commit()

    # Fetch last 10 messages for context
    messages = ChatMessage.query.filter_by(chat_id=chat.id).order_by(ChatMessage.created_at.desc()).limit(10).all()
    messages = list(reversed(messages))  # Oldest first
    context = [m.content for m in messages if m.sender == "user" or m.sender == "ai"]

    # Conversational logic with Infermedica, pass context and answers_dict
    state = chat.state or {}
    ai_message = infermedica_conversational_flow(state, user_message, context=context, answers_dict=answers_dict, callback=callback)
    fallback_phrases = [
        "I don't know",
        "I'm sorry",
        "I am not sure",
        "As an AI language model",
        "I cannot answer"
    ]
    hidden = any(phrase.lower() in ai_message.lower() for phrase in fallback_phrases)
    
    # Store the AI message in the database
    ai_msg = ChatMessage(chat_id=chat.id, sender="ai", content=ai_message)
    db.session.add(ai_msg)

    # Persist updated state in the chat record
    chat.state = state
    chat.updated_at = datetime.datetime.utcnow()
    db.session.commit()

    # If the state has a last_question, return it as a structured followup
    followup = None
    if state.get("last_question"):
        q = state["last_question"]
        followup = {
            "text": q.get("text"),
            "items": [
                {
                    "name": item.get("name", ""),
                    "choices": [c["label"] for c in item.get("choices", [])],
                    "type": item.get("type", "single")
                } for item in q.get("items", [])
            ],
            "callback": callback  # Pass the callback to the frontend
        }

    return jsonify({
        "ai_message": "" if hidden else ai_message,
        "hidden": hidden,
        "raw_message": ai_message,
        "followup": followup,  # always present if last_question is set
        "callback": callback  # Return the callback for frontend state management
    })

# --- Health Check Endpoint ---
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

# --- Utility: Translate to English ---
@app.route('/api/utils/translate', methods=['POST'])
def api_translate():
    data = request.get_json()
    text = data.get('text', '')
    translated = translate_to_english(text)
    return jsonify({'translated': translated})

# --- Utility: Detect Language ---
@app.route('/api/utils/detect_language', methods=['POST'])
def api_detect_language():
    data = request.get_json()
    text = data.get('text', '')
    lang = detect_language(text)
    return jsonify({'lang': lang})

# --- Utility: Extract Text from File (PDF/Image/Audio) ---
@app.route('/api/utils/extract', methods=['POST'])
def api_extract():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    filename = file.filename.lower()
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        file.save(tmp.name)
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(tmp.name)
        elif filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
            from utils import process_image
            text = process_image(tmp.name)
        elif filename.endswith('.wav') or filename.endswith('.mp3') or filename.endswith('.m4a'):
            from utils import process_audio
            text = process_audio(tmp.name)
        else:
            text = ''
    return jsonify({'text': text})

# --- OpenAI Completion Endpoint ---
@app.route('/api/openai', methods=['POST'])
def api_openai():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        response = get_openai_response(prompt)
        # Hide fallback/default responses from user
        fallback_phrases = [
            "I don't know",
            "I'm sorry",
            "I am not sure",
            "As an AI language model",
            "I cannot answer"
        ]
        hide = any(phrase.lower() in response.lower() for phrase in fallback_phrases)
        return jsonify({'response': '' if hide else response, 'raw_response': response, 'hidden': hide})
    except Exception as e:
        print("OpenAI endpoint error:", e)
        return jsonify({'error': str(e)}), 500

# --- Image Generation Endpoint ---
@app.route('/generate_image', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        # Use OpenAI DALL-E API
        if not os.getenv("OPENAI_API_KEY"):
            return jsonify({'error': 'OpenAI API key not set'}), 500
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        image_url = response['data'][0]['url']
        return jsonify({'image_url': image_url})
    except Exception as e:
        print("Image generation error:", e)
        return jsonify({'error': str(e)}), 500

# --- TTS Endpoint ---
@app.route('/tts', methods=['POST'])
def tts():
    try:
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        # Generate TTS audio using gTTS
        audio_dir = os.path.join(app.root_path, 'static', 'audio')
        os.makedirs(audio_dir, exist_ok=True)
        filename = f"tts_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(audio_dir, filename)
        tts = gTTS(text)
        tts.save(filepath)
        audio_url = f"/static/audio/{filename}"
        return jsonify({'audio_url': audio_url})
    except Exception as e:
        print("TTS error:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

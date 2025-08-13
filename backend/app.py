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

CORS(app, resources={r"/api/*": {"origins": ["https://project-bmx.streamlit.app/"]}})

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
def send_message(chat_id):
    try:
        chat = Chat.query.get_or_404(chat_id)
        user_id = str(get_jwt_identity())
        if str(chat.user_id) != user_id:
            return jsonify({"error": "Unauthorized"}), 403
            
        data = request.get_json()
        content = data.get('content', '')
        context = data.get('context', [])
        answers_dict = data.get('answers')
        callback = data.get('callback')
        
        logging.info(f"Received message request - Content: {content}")
        logging.info(f"Context: {context}")
        logging.info(f"Answers dict: {answers_dict}")
        
        # Add user message to chat
        user_message = ChatMessage(
            chat_id=chat_id,
            content=content,
            sender='user'
        )
        db.session.add(user_message)
        
        # Initialize response variables
        ai_message = None
        followup = None
        new_state = None
        
        try:
            # First try to get response from OpenAI
            openai_response = get_openai_response(content)
            if openai_response and not any(phrase in openai_response.lower() for phrase in ["i don't know", "i'm sorry", "i am not sure", "as an ai", "i cannot"]):
                ai_message = openai_response
            else:
                # If OpenAI response is not suitable, try infermedica
                infermedica_response = infermedica_conversational_flow(
                    chat.state or {},
                    content,
                    context=context,
                    answers_dict=answers_dict,
                    callback=callback
                )
                
                if isinstance(infermedica_response, dict):
                    ai_message = infermedica_response.get('text', '')
                    followup = infermedica_response
                    if 'state' in infermedica_response:
                        new_state = infermedica_response['state']
                else:
                    ai_message = infermedica_response
        except Exception as e:
            logging.error(f"Error getting AI response: {str(e)}")
            ai_message = "I'm having trouble processing your request right now. Please try again in a moment."
            
        if not ai_message:
            ai_message = "I apologize, but I couldn't generate a response. Please try again."
            
        logging.info(f"AI Response: {ai_message}")
        
        # Add AI message to chat
        ai_message_obj = ChatMessage(
            chat_id=chat_id,
            content=ai_message,
            sender='ai'
        )
        db.session.add(ai_message_obj)
        
        # Update chat state if we have a new state
        if new_state:
            chat.state = new_state
        chat.updated_at = datetime.datetime.now(datetime.UTC)
        db.session.commit()
        
        response_data = {
            'ai_message': ai_message,
            'hidden': False,
            'raw_message': ai_message,
            'followup': followup,
            'callback': callback,
            'is_question': bool(followup)
        }
        
        logging.info(f"Sending response: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        logging.error(f"Error in send_message: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

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
        app.logger.warning("No file uploaded in request.")
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    filename = file.filename.lower()
    app.logger.info(f"Received file: {filename}")
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[-1]) as tmp:
        file.save(tmp.name)
        file_size = os.path.getsize(tmp.name)
        app.logger.info(f"Saved file to temp: {tmp.name} (size: {file_size} bytes)")
        try:
            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(tmp.name)
                app.logger.info(f"PDF extraction result length: {len(text)} chars")
                if not text.strip():
                    app.logger.warning(f"PDF extraction returned empty text for file: {filename}")
            elif filename.endswith(('.jpg', '.jpeg', '.png')):
                from utils import process_image
                try:
                    text = process_image(tmp.name)
                    app.logger.info(f"Image OCR result length: {len(text)} chars")
                    if not text.strip():
                        app.logger.warning(f"Image OCR returned empty text for file: {filename}")
                except Exception as e:
                    app.logger.error(f"Image processing error: {str(e)}")
                    text = f"Image processing error: {str(e)}"
            elif filename.endswith(('.wav', '.mp3', '.m4a')):
                from utils import process_audio
                try:
                    text = process_audio(tmp.name)
                    app.logger.info(f"Audio transcription result length: {len(text)} chars")
                    if not text.strip():
                        app.logger.warning(f"Audio transcription returned empty text for file: {filename}")
                except Exception as e:
                    app.logger.error(f"Audio processing error: {str(e)}")
                    text = f"Audio processing error: {str(e)}"
            else:
                app.logger.warning(f"Unsupported file type: {filename}")
                text = ''
        except Exception as e:
            app.logger.error(f"General extraction error for file {filename}: {str(e)}", exc_info=True)
            text = f"General extraction error: {str(e)}"
    app.logger.info(f"Final extracted text length: {len(text)} chars for file: {filename}")
    return jsonify({'text': text})

# --- OpenAI Completion Endpoint ---
@app.route('/api/openai', methods=['POST'])
def api_openai():
    try:
        data = request.get_json()
        text = data.get('prompt', '')
        response = get_openai_response(text)
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
        text = data.get('prompt', '')
        if not text:
            return jsonify({'error': 'No prompt provided'}), 400
        # Use OpenAI DALL-E API
        if not os.getenv("OPENAI_API_KEY"):
            return jsonify({'error': 'OpenAI API key not set'}), 500
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.Image.create(
            prompt=text,
            n=1,
            size="512x512"
        )
        image_url = response['data'][0]['url']
        return jsonify({'image_url': image_url})
    except Exception as e:
        print("Image generation error:", e)
        return jsonify({'error': str(e)}), 500

# --- TTS Endpoint ---
@app.route('/api/tts', methods=['POST'])
@jwt_required()
def tts():
    try:
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({'error': 'No text provided'}), 400
            
        # Create static and audio directories if they don't exist
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        audio_dir = os.path.join(static_dir, 'audio')
        os.makedirs(audio_dir, exist_ok=True)
        
        # Generate unique filename
        filename = f"tts_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(audio_dir, filename)
        
        # Generate TTS audio
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filepath)
        
        # Return the full URL for the audio file
        audio_url = f"{request.host_url}api/static/audio/{filename}"
        return jsonify({'audio_url': audio_url})
        
    except Exception as e:
        logging.error(f"TTS error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

# Serve static files
@app.route('/api/static/<path:filename>')
def serve_static(filename):
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    return send_from_directory(static_dir, filename)

if __name__ == "__main__":
    app.run(debug=True)
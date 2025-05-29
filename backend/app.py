from dotenv import load_dotenv
import os
import base64
from PIL import Image
import io
import speech_recognition as sr
import tempfile
import wave
import numpy as np
import time
from pydub import AudioSegment

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
from utils import detect_language, translate_to_english, extract_text_from_file
from openai_client import get_openai_response
import datetime
import logging
import uuid
from gtts import gTTS
from gtts.tts import gTTSError

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB
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
            user = db.session.get(User, user_id)
            if not user:
                return jsonify({"error": "User not found"}), 401
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
        # Get and validate user identity
        try:
            user_id = int(get_jwt_identity())
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid user ID format"}), 401

        # Get and validate chat
        chat = db.session.get(Chat, chat_id)
        if not chat:
            return jsonify({"error": "Chat not found"}), 404
        if chat.user_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        # Rest of existing processing logic
        data = request.get_json()
        content = data.get('content', '')
        context = data.get('context', [])
        answers_dict = data.get('answers')
        callback = data.get('callback')
        logging.info(f"Received message request - Content: {content}")
        logging.info(f"Context: {context}")
        logging.info(f"Answers dict: {answers_dict}")
        user_message = ChatMessage(
            chat_id=chat_id,
            content=content,
            sender='user'
        )
        db.session.add(user_message)
        ai_message = None
        followup = None
        new_state = None
        try:
            openai_response = get_openai_response(content)
            if openai_response and not any(phrase in openai_response.lower() for phrase in ["i don't know", "i'm sorry", "i am not sure", "as an ai", "i cannot"]):
                ai_message = openai_response
            else:
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
        ai_message_obj = ChatMessage(
            chat_id=chat_id,
            content=ai_message,
            sender='ai'
        )
        db.session.add(ai_message_obj)
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
        logging.error(f"Error in send_message: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

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
@jwt_required()
def handle_file_extraction():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'Empty filename'}), 400

    file_type = file.filename.split('.')[-1].lower()
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        result = extract_text_from_file(tmp_path, file_type)
        return jsonify({'text': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        try:
            os.unlink(tmp_path)
        except Exception as e:
            logging.warning(f"Could not delete temp file: {e}")


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
@app.route('/api/tts', methods=['POST'])
@jwt_required()
def tts():
    try:
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({'error': 'No text provided'}), 400

        max_text_length = 500
        if len(text) > max_text_length:
            text = text[:max_text_length] + "..."

        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        audio_dir = os.path.join(static_dir, 'audio')
        os.makedirs(audio_dir, exist_ok=True)

        filename = f"tts_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(audio_dir, filename)
        logging.info(f"TTS request: text='{text[:50]}...', target filepath='{filepath}'")

        max_retries = 3
        retry_delay = 1
        file_generated_successfully = False

        for attempt in range(max_retries):
            logging.info(f"TTS attempt {attempt + 1}/{max_retries} for filepath='{filepath}'")
            try:
                tts_instance = gTTS(
                    text=text,
                    lang='en',
                    slow=False,
                    timeout=10 # Increased timeout for gTTS
                )
                logging.info(f"TTS attempt {attempt + 1}: Saving to {filepath}")
                tts_instance.save(filepath)
                logging.info(f"TTS attempt {attempt + 1}: Saved to {filepath}. Checking existence and size.")

                if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                    logging.info(f"TTS attempt {attempt + 1}: File {filename} created successfully at {filepath}. Size: {os.path.getsize(filepath)}. Re-verifying after short delay.")
                    time.sleep(0.05) # 50ms delay

                    if not (os.path.exists(filepath) and os.path.getsize(filepath) > 0):
                        logging.error(f"TTS CRITICAL: File {filename} at {filepath} existed but disappeared or became empty within 50ms! Initial size was > 0.")
                        raise Exception("TTS file vanished or became empty immediately after creation and initial check")

                    audio_url = f"{request.host_url}api/static/audio/{filename}"
                    file_generated_successfully = True
                    logging.info(f"TTS file {filename} re-verified and confirmed at {filepath}. URL: {audio_url}. Returning success.")
                    return jsonify({'audio_url': audio_url})
                else:
                    size_if_exists = os.path.getsize(filepath) if os.path.exists(filepath) else -1
                    logging.warning(f"TTS attempt {attempt + 1}: File {filepath} is empty (size: {size_if_exists}) or missing after save.")
                    if os.path.exists(filepath):
                        try:
                            logging.info(f"TTS attempt {attempt + 1}: Deleting invalid (empty/partial) file {filepath} before raising error for retry.")
                            os.unlink(filepath)
                        except Exception as del_e:
                            logging.warning(f"Error unlinking invalid TTS file {filepath} during attempt {attempt + 1} cleanup: {del_e}")
                    raise Exception("Generated audio file is empty or missing after save attempt")

            except gTTSError as e:
                logging.error(f"TTS gTTSError (attempt {attempt + 1}/{max_retries}) for {filepath}: {str(e)}", exc_info=True)
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    if os.path.exists(filepath):
                        try:
                            logging.info(f"TTS gTTSError: Cleaning up failed/partial file {filepath} before retry {attempt + 2}.")
                            os.unlink(filepath)
                        except Exception as del_e:
                            logging.warning(f"Error unlinking partial TTS file {filepath} before retry (gTTSError): {del_e}")
                    continue
                else:
                    logging.error(f"TTS gTTSError: Max retries reached for text: {text[:50]}... Filepath was: {filepath}")
                    return jsonify({'error': 'TTS service unavailable. Please try again later.'}), 503

            except Exception as e:
                logging.error(f"Unexpected TTS error (attempt {attempt + 1}/{max_retries}) for {filepath}: {str(e)}", exc_info=True)
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    if os.path.exists(filepath):
                        try:
                            logging.info(f"TTS Exception: Cleaning up failed/partial file {filepath} before retry {attempt + 2}.")
                            os.unlink(filepath)
                        except Exception as del_e:
                            logging.warning(f"Error unlinking partial TTS file {filepath} before retry (Exception): {del_e}")
                    continue
                else:
                    logging.error(f"TTS Exception: Max retries reached for text: {text[:50]}... Filepath was: {filepath}")
                    return jsonify({'error': 'Error generating speech. Please try again.'}), 500
            finally:
                logging.debug(f"TTS finally block for attempt {attempt + 1}. file_generated_successfully: {file_generated_successfully}, filepath: {filepath}")
                pass # Explicit pass

        logging.error(f"TTS: Failed to generate speech for text '{text[:50]}...' after {max_retries} attempts. Filepath was: {filepath}")
        return jsonify({'error': 'Failed to generate speech after multiple attempts'}), 500

    except Exception as e:
        logging.error(f"Outer TTS error: {str(e)} for text '{text[:50]}...'", exc_info=True)
        if 'filepath' in locals() and os.path.exists(filepath) and not file_generated_successfully:
            try:
                logging.warning(f"Outer TTS error: Cleaning up potentially orphaned file {filepath}")
                os.unlink(filepath)
            except Exception as del_e:
                logging.warning(f"Outer TTS error: Failed to clean up orphaned file {filepath}: {del_e}")
        return jsonify({'error': 'An unexpected error occurred during text-to-speech processing.'}), 500

# Add cleanup function for old audio files
def cleanup_old_audio_files():
    """Clean up audio files older than 1 hour"""
    try:
        audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'audio')
        logging.info(f"Cleanup: Starting cleanup in directory: {audio_dir}")
        if not os.path.exists(audio_dir):
            logging.info(f"Cleanup: Audio directory {audio_dir} does not exist. Skipping cleanup.")
            return

        current_time = time.time()
        for filename in os.listdir(audio_dir):
            if filename.startswith('tts_'):
                filepath = os.path.join(audio_dir, filename)
                file_mod_time = os.path.getmtime(filepath)
                age_seconds = current_time - file_mod_time
                logging.info(f"Cleanup: Checking file {filepath}, age: {age_seconds:.2f} seconds")
                # Check if file is older than 1 hour
                if age_seconds > 3600:
                    logging.info(f"Cleanup: Deleting old audio file {filepath} (age: {age_seconds:.2f} seconds)")
                    try:
                        os.unlink(filepath)
                        logging.info(f"Cleanup: Successfully deleted {filepath}")
                    except Exception as e:
                        logging.warning(f"Cleanup: Error deleting old audio file {filename}: {str(e)}")
                else:
                    logging.info(f"Cleanup: Keeping file {filepath} (age: {age_seconds:.2f} seconds)")
    except Exception as e:
        logging.error(f"Cleanup: Error in cleanup_old_audio_files: {str(e)}")

# Call cleanup function periodically
@app.before_request
def before_request():
    logging.info("Before request: Calling cleanup_old_audio_files()")
    cleanup_old_audio_files()

# Serve static files
@app.route('/api/static/<path:path>') # Changed filename to path to match directory structure
def serve_static(path):
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    requested_file_path = os.path.join(static_dir, path)
    logging.info(f"ServeStatic: Attempting to serve file. Requested path: {path}")
    logging.info(f"ServeStatic: Static directory: {static_dir}")
    logging.info(f"ServeStatic: Resolved full path: {requested_file_path}")
    if os.path.exists(requested_file_path):
        logging.info(f"ServeStatic: File {requested_file_path} exists. Serving.")
    else:
        logging.warning(f"ServeStatic: File {requested_file_path} NOT FOUND.")
    return send_from_directory(static_dir, path) # Changed filename to path

# --- Process Voice Input Endpoint ---
@app.route('/api/process_voice', methods=['POST'])
@jwt_required()
def process_voice():
    temp_audio_path = None
    temp_original_path = None
    try:
        # Log request details
        logging.info(f"Received voice processing request")
        logging.info(f"Request files: {list(request.files.keys())}")
        
        # Check if audio file is in request
        if 'audio' not in request.files:
            logging.error("No audio file in request")
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files['audio']
        logging.info(f"Audio file: {audio_file}")
        logging.info(f"Audio filename: {audio_file.filename}")
        logging.info(f"Audio content type: {audio_file.content_type}")
        
        if not audio_file.filename:
            logging.error("Empty audio filename")
            return jsonify({"error": "No selected file"}), 400

        # Create a temporary file to store the original audio
        temp_original = tempfile.NamedTemporaryFile(delete=False)
        temp_original_path = temp_original.name
        temp_original.close()
        
        # Save the original audio file
        audio_file.save(temp_original_path)
        
        # Check file size
        file_size = os.path.getsize(temp_original_path)
        logging.info(f"Saved audio file, size: {file_size} bytes")
        
        if file_size == 0:
            logging.error("Audio file is empty")
            try:
                os.unlink(temp_original_path)
            except:
                pass
            return jsonify({"error": "Audio file is empty"}), 400
        
        # Create a temporary file for the converted WAV audio
        temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_audio_path = temp_audio.name
        temp_audio.close()
        
        # Convert audio to WAV format using pydub
        try:
            # Try to load the audio file (pydub can handle many formats)
            audio_segment = AudioSegment.from_file(temp_original_path)
            
            # Convert to WAV format with settings compatible with speech_recognition
            audio_segment = audio_segment.set_frame_rate(16000)  # 16kHz sample rate
            audio_segment = audio_segment.set_channels(1)        # Mono
            audio_segment = audio_segment.set_sample_width(2)    # 16-bit
            
            # Export as WAV
            audio_segment.export(temp_audio_path, format="wav")
            
            logging.info(f"Successfully converted audio file to WAV format")
            
        except Exception as conversion_error:
            logging.error(f"Audio conversion error: {str(conversion_error)}", exc_info=True)
            error_message = f"Audio format conversion failed. Original error: {str(conversion_error)}"
            if "ffmpeg" in str(conversion_error).lower() or "avconv" in str(conversion_error).lower() or "couldn't find" in str(conversion_error).lower():
                error_message += " This might be due to FFmpeg not being installed or found. Please ensure FFmpeg is installed and in your system's PATH."
            
            # Clean up temp files
            try:
                if temp_original_path and os.path.exists(temp_original_path):
                    os.unlink(temp_original_path)
            except Exception as e:
                logging.warning(f"Error cleaning up temp_original_path during conversion error: {str(e)}")
            return jsonify({"error": error_message}), 400
        
        # Clean up the original temp file (if conversion was successful)
        try:
            os.unlink(temp_original_path)
        except:
            pass
        
        # Initialize speech recognizer
        recognizer = sr.Recognizer()
        
        # Adjust recognition parameters for better accuracy
        recognizer.energy_threshold = 100  # Lower threshold to detect quieter speech
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.5  # Shorter pause threshold
        recognizer.phrase_threshold = 0.3  # Lower phrase threshold
        recognizer.non_speaking_duration = 0.3  # Shorter non-speaking duration
        
        # Process the audio file
        with sr.AudioFile(temp_audio_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            
            # Record the audio
            audio = recognizer.record(source)
            
            # Attempt to recognize speech with multiple attempts
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    text = recognizer.recognize_google(
                        audio,
                        language='en-US',  # Specify language
                        show_all=False  # Return only the most likely result
                    )
                    
                    if text and text.strip():
                        return jsonify({"text": text.strip()})
                    
                    # If we get here, the text was empty
                    if attempt < max_attempts - 1:
                        logging.warning(f"Empty text result, attempt {attempt + 1}/{max_attempts}")
                        continue
                    else:
                        return jsonify({"error": "No speech detected in audio"}), 400
                        
                except sr.UnknownValueError:
                    if attempt < max_attempts - 1:
                        logging.warning(f"Unknown value error, attempt {attempt + 1}/{max_attempts}")
                        continue
                    else:
                        return jsonify({"error": "Could not understand audio. Please try speaking more clearly."}), 400
                        
                except sr.RequestError as e:
                    logging.error(f"Speech recognition service error: {str(e)}", exc_info=True)
                    if attempt < max_attempts - 1:
                        logging.warning(f"Request error, attempt {attempt + 1}/{max_attempts}")
                        continue
                    else:
                        return jsonify({"error": "Speech recognition service is currently unavailable. Please try again later."}), 503
                    
    except Exception as e:
        logging.error(f"Error processing voice input: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error. Please try again."}), 500
        
    finally:
        # Clean up both temporary files
        for temp_file in [temp_audio_path, temp_original_path]:
            if temp_file and os.path.exists(temp_file):
                try:
                    # Wait a short time to ensure file is not in use
                    time.sleep(0.1)
                    os.unlink(temp_file)
                    logging.info(f"Cleaned up temporary file: {temp_file}")
                except Exception as e:
                    logging.warning(f"Error cleaning up temporary file {temp_file}: {str(e)}")

# --- Process Image Input Endpoint ---
@app.route('/api/process_image', methods=['POST'])
@jwt_required()
def process_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']
        if not image_file.filename:
            return jsonify({"error": "No selected file"}), 400

        # Read and process the image
        image = Image.open(image_file)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too large (max 1024x1024)
        max_size = 1024
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Save processed image to temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_img:
            image.save(temp_img.name, 'JPEG', quality=85)
            
            # Generate a unique filename
            filename = f"{uuid.uuid4()}.jpg"
            save_path = os.path.join(app.static_folder, 'uploads', filename)
            
            # Ensure uploads directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Move the temporary file to the uploads directory
            os.rename(temp_img.name, save_path)
            
            # Return the URL for the processed image
            image_url = f"/api/static/uploads/{filename}"
            return jsonify({
                "image_url": image_url,
                "message": "Image processed successfully"
            })

    except Exception as e:
        logging.error(f"Error processing image: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# --- Extract Text from Image Endpoint ---
@app.route('/api/extract_text_from_image', methods=['POST'])
@jwt_required()
def extract_text_from_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']
        if not image_file.filename:
            return jsonify({"error": "No selected file"}), 400

        # Save image to temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_img:
            image_file.save(temp_img.name)
            
            # Use OpenAI's vision model to extract text
            try:
                with open(temp_img.name, 'rb') as img_file:
                    # Convert image to base64
                    img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                    
                    # Call OpenAI API for text extraction
                    response = get_openai_response(
                        f"Extract all text from this image: data:image/jpeg;base64,{img_base64}",
                        model="gpt-4-vision-preview"
                    )
                    
                    return jsonify({"text": response})
            finally:
                # Clean up the temporary file
                os.unlink(temp_img.name)

    except Exception as e:
        logging.error(f"Error extracting text from image: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# --- Generate Chat Title Endpoint ---
@app.route('/api/chats/<int:chat_id>/title', methods=['POST'])
@jwt_required()
def generate_chat_title(chat_id):
    try:
        user_id = int(get_jwt_identity())
        chat = db.session.get(Chat, chat_id)
        if not chat or chat.user_id != user_id:
            return jsonify({"error": "Unauthorized or chat not found"}), 403
        data = request.get_json()
        user_message = data.get('user_message', '')
        from openai_client import get_chat_title
        title = get_chat_title(user_message)
        chat.title = title
        db.session.commit()
        return jsonify({"title": title})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
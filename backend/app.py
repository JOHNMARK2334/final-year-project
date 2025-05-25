from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate
from flask_cors import CORS
from functools import wraps
from models import db, Chat, ChatMessage, User
from infermedica_conversation import infermedica_conversational_flow
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os
import logging

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
    chat = Chat.query.get_or_404(chat_id)
    if chat.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    # Save user message
    msg = ChatMessage(chat_id=chat.id, sender="user", content=user_message)
    db.session.add(msg)
    db.session.commit()

    # Conversational logic with Infermedica
    state = chat.state or {}
    ai_message = infermedica_conversational_flow(state, user_message)
    if not ai_message or not ai_message.strip():
        ai_message = "I'm still processing your information. Please provide more details about your symptoms or answer the previous question."
    ai_msg = ChatMessage(chat_id=chat.id, sender="ai", content=ai_message)
    db.session.add(ai_msg)

    # Persist updated state in the chat record
    chat.state = state
    chat.updated_at = datetime.datetime.utcnow()
    db.session.commit()
    return jsonify({"ai_message": ai_message})

# --- Health Check Endpoint ---
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)

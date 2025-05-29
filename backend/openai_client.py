import os
from openai import OpenAI
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logging.error("OPENAI_API_KEY not found in environment variables")
    raise ValueError("OPENAI_API_KEY environment variable is not set")

def get_openai_response(prompt):
    try:
        client = OpenAI(api_key=api_key)
        system_message = {"role": "system", "content": "You are a helpful medical assistant. Provide informative and helpful responses about health and medical topics. Always maintain a professional and caring tone. If you're unsure about something, acknowledge the limitations and suggest consulting a healthcare professional."}
        user_message = {"role": "user", "content": prompt}
        messages = [system_message, user_message]
        max_tokens = 8192
        all_content = ""
        for _ in range(5):  # up to 5 continuations if needed
            response = client.chat.completions.create(
                model="gpt-4.1-2025-04-14",
                messages=messages,
                temperature=0.7,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content.strip()
            all_content += content
            finish_reason = getattr(response.choices[0], 'finish_reason', None)
            if finish_reason != 'length':
                break
            # If truncated, add 'continue' and ask for more
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user", "content": "Continue."})
        return all_content
    except Exception as e:
        logging.error(f"OpenAI API error: {str(e)}")
        return None

def get_chat_title(user_message):
    """Generate a concise, unique chat title from the first user message."""
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4.1-2025-04-14",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Given the user's first message, generate a short, unique, and descriptive chat title (max 6 words) that summarizes the user's intent or question. Do not use generic titles like 'New Chat' or 'Conversation'."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=16
        )
        return response.choices[0].message.content.strip().replace('"', '')
    except Exception as e:
        logging.error(f"OpenAI chat title error: {str(e)}")
        return "Untitled Chat"
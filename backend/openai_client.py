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

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

def get_openai_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a highly knowledgeable and helpful medical assistant. "
                        "Provide accurate, detailed, and well-researched answers to user queries about health and medical topics. "
                        "Cite relevant sources or guidelines when possible. "
                        "If the user requests, provide step-by-step explanations, lists, or summaries. "
                        "Always maintain a professional, caring, and clear tone. "
                        "If you are unsure, acknowledge limitations and recommend consulting a healthcare professional. "
                        "If the user asks for more detail, expand your answer with additional context, examples, or references."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=700
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"OpenAI API error: {str(e)}")
        return None
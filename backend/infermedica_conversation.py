import requests
import os
import logging
import difflib
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logging.error("OPENAI_API_KEY not found in environment variables")
    raise ValueError("OPENAI_API_KEY environment variable is not set")


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

INFERMEDICA_API_URL = "https://api.infermedica.com/v3"
INFERMEDICA_HEADERS = None

def get_infermedica_headers():
    global INFERMEDICA_HEADERS
    if INFERMEDICA_HEADERS is not None:
        return INFERMEDICA_HEADERS
        
    app_id = os.getenv("INFERMEDICA_APP_ID")
    app_key = os.getenv("INFERMEDICA_APP_KEY")
    
    if not app_id or not app_key:
        logger.error("Infermedica API keys are not set")
        return None
        
    INFERMEDICA_HEADERS = {
        "App-Id": app_id,
        "App-Key": app_key,
        "Content-Type": "application/json"  
    }
    return INFERMEDICA_HEADERS

client = OpenAI(api_key=api_key)

def get_openai_response(text):
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
                {"role": "user", "content": text}
            ],
            temperature=0.7,
            max_tokens=700
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"OpenAI API error: {str(e)}")
        return None
    
def get_diagnosis(evidence, sex, age):
    headers = get_infermedica_headers()
    if not headers:
        return None
        
    try:
        resp = requests.post(
            f"{INFERMEDICA_API_URL}/diagnosis",
            headers=headers,
            json={
                "sex": sex,
                "age": {"value": age},
                "evidence": evidence
            }
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"Diagnosis request error: {str(e)}")
        return None

def infermedica_conversational_flow(state, user_message, context=None, answers_dict=None, callback=None):
    try:
        # Initialize state if not present
        if not state:
            state = {
                "evidence": [],
                "sex": "male",  # Default values
                "age": 30
            }
        
        # Get headers
        headers = get_infermedica_headers()
        if not headers:
            return "Medical reasoning engine is not configured. Please contact the administrator."

        # Parse the user message to extract symptoms
        parse_payload = {
            "text": user_message,
            "sex": state["sex"],
            "age": {"value": state["age"]}
        }
        
        try:
            parse_resp = requests.post(
                f"{INFERMEDICA_API_URL}/parse",
                json=parse_payload,
                headers=headers
            )
            parse_resp.raise_for_status()
            parse_json = parse_resp.json()
            
            # Add any found symptoms to evidence
            if "mentions" in parse_json:
                for mention in parse_json["mentions"]:
                    if mention.get("type") == "symptom":
                        symptom_id = mention["id"]
                        choice_id = mention.get("choice_id", "present")
                        state["evidence"].append({
                            "id": symptom_id,
                            "choice_id": choice_id,
                            "initial": True
                        })
        except Exception as e:
            logger.error(f"Error in parse request: {str(e)}")
        
        # Get diagnosis
        diagnosis = get_diagnosis(state["evidence"], state["sex"], state["age"])
        
        if diagnosis and diagnosis.get("conditions"):
            # Format the diagnosis response
            conditions = diagnosis["conditions"]
            response = "Based on your symptoms, here are the possible conditions:\n\n"
            
            for condition in conditions[:3]:  # Show top 3 conditions
                probability = round(condition["probability"] * 100, 1)
                response += f"- {condition['common_name']} ({probability}% probability)\n"
            
            response += "\nRecommendations:\n"
            response += "1. Please consult with a healthcare professional for proper diagnosis and treatment.\n"
            response += "2. If symptoms worsen or you experience severe symptoms, seek immediate medical attention.\n"
            
            return response
        else:
            # If no diagnosis from Infermedica, try OpenAI
            openai_response = get_openai_response(user_message)
            if openai_response:
                return openai_response
            else:
                return "I apologize, but I couldn't provide a specific diagnosis. Please consult with a healthcare professional for proper medical advice."
                
    except Exception as e:
        logger.error(f"Error in conversation flow: {str(e)}")
        return "I apologize, but I encountered an error. Please try again or consult with a healthcare professional."
import openai
import os
import logging

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logging.error("OPENAI_API_KEY is not set in environment variables.")

client = openai.OpenAI(api_key = OPENAI_API_KEY)

def get_openai_response(prompt):
    try:
        if not OPENAI_API_KEY:
            return "OpenAI API is not configured. Please contact the administrator."
        
        # Handle empty or greeting prompts
        if not prompt.strip() or prompt.lower().strip() in ['hello', 'hi', 'hey']:
            return "Hello! I'm your health assistant. Please describe your symptoms so I can help you better."
        
        response = client.chat.completions.create(
            model="gpt-4.1-2025-04-14",
            messages=[
                {
                    "role": "system",
                    "content": """You are an AI medical assistant. Provide general health information but always:
                    1. Clarify you're not a doctor
                    2. Diagnose or prescribe treatments if necessary
                    3. Recommend consulting a healthcare professional
                    4. For emergencies, advise immediate medical attention"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=256
        )
        
        # Add disclaimer if not already present
        response_text = response.choices[0].message.content
        if "I'm not a doctor" not in response_text and "consult a healthcare professional" not in response_text:
            response_text += "\n\nRemember, I'm an AI assistant and not a doctor. For proper medical advice, please consult a healthcare professional."
            
        return response_text
        
    except Exception as e:
        return f"I encountered an error processing your request. Please try again. Error: {str(e)}"
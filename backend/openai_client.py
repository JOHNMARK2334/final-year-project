import openai

client = openai.OpenAI(api_key = "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")

def get_openai_response(prompt):
    try:
        # Handle empty or greeting prompts
        if not prompt.strip() or prompt.lower().strip() in ['hello', 'hi', 'hey']:
            return "Hello! I'm your health assistant. Please describe your symptoms so I can help you better."
        
        response = client.chat.completions.create(
            model="gpt-4",
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
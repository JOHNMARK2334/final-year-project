import requests
import os
import logging
import difflib
from datetime import datetime

# Configure logging with more detailed format
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
    
    logger.info(f"Checking Infermedica API keys - App ID exists: {bool(app_id)}, App Key exists: {bool(app_key)}")
    
    if not app_id or not app_key:
        logger.error("Infermedica API keys are not set. Please set INFERMEDICA_APP_ID and INFERMEDICA_APP_KEY in your environment.")
        return None
        
    INFERMEDICA_HEADERS = {
        "App-Id": app_id,
        "App-Key": app_key,
        "Content-Type": "application/json"  
    }
    return INFERMEDICA_HEADERS

def get_info_infermedica(text, sex, age):
    headers = get_infermedica_headers()
    if not headers:
        return {}
    try:
        resp = requests.post(
            "https://api.infermedica.com/v3/info",
            headers=headers,
            json={"text": text, "sex": sex, "age": {"value": age}}
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {}

def parse_infermedica(text, sex, age):
    headers = get_infermedica_headers()
    if not headers:
        return {}
    try:
        resp = requests.post(
            "https://api.infermedica.com/v3/parse",
            headers=headers,
            json={"text": text, "sex": sex, "age": {"value": age}}
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {}

def search_infermedica(phrase, sex, age):
    headers = get_infermedica_headers()
    if not headers:
        return []
    try:
        resp = requests.get(
            "https://api.infermedica.com/v3/search",
            headers=headers,
            params={"phrase": phrase, "sex": sex, "age.value": age}
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return []

def get_symptom_details(symptom_id):
    headers = get_infermedica_headers()
    if not headers:
        return {}
    try:
        resp = requests.get(
            f"https://api.infermedica.com/v3/symptoms/{symptom_id}",
            headers=headers
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}

def get_risk_factor_details(risk_factor_id):
    headers = get_infermedica_headers()
    if not headers:
        return {}
    try:
        resp = requests.get(
            f"https://api.infermedica.com/v3/risk_factors/{risk_factor_id}",
            headers=headers
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}

def fuzzy_match(user_input, choices):
    # Return the best match if similarity > 0.7, else None
    user_input = user_input.lower()
    best = None
    best_score = 0.0
    for choice in choices:
        score = difflib.SequenceMatcher(None, user_input, choice.lower()).ratio()
        if score > best_score:
            best_score = score
            best = choice
    if best_score > 0.7:
        return best
    # Also allow partial match
    for choice in choices:
        if choice.lower() in user_input or user_input in choice.lower():
            return choice
    return None

def infermedica_conversational_flow(state, user_message, context=None, answers_dict=None, callback=None):
    """
    Fixed function signature and response structure
    """
    try:
        logger.info(f"Starting conversation flow with message: {user_message}")
        logger.info(f"Current state: {state}")
        logger.info(f"Answers dict: {answers_dict}")
        
        # Initialize state if not present
        if not state:
            state = {
                "evidence": [],
                "risk_factors": [],
                "last_question": None,
                "last_followup": None,
                "current_callback": None,
                "answered_questions": set(),
                "conversation_start": datetime.now().isoformat(),
                "last_interaction": datetime.now().isoformat(),
                "sex": "male",  # Default values
                "age": 30
            }
            logger.info("Initialized new conversation state")
        
        # Update last interaction time
        state["last_interaction"] = datetime.now().isoformat()
        
        # Store callback in state
        if callback:
            state["current_callback"] = callback
            logger.info(f"Stored callback: {callback}")

        # Get headers first
        headers = get_infermedica_headers()
        if not headers:
            logger.error("Failed to get Infermedica headers")
            return "Medical reasoning engine is not configured. Please contact the administrator."

        # Process answers from follow-up questions first
        if answers_dict and state.get("last_question"):
            logger.info("Processing answers from follow-up question")
            q = state["last_question"]
            
            # Process each answer in the answers_dict
            for question_text, answer in answers_dict.items():
                # Find the corresponding symptom/item ID
                if q.get("type") == "single":
                    if str(answer).lower() in ["yes", "present"]:
                        choice_id = "present"
                    elif str(answer).lower() in ["no", "absent"]:
                        choice_id = "absent"
                    else:
                        choice_id = "unknown"
                    
                    state["evidence"].append({
                        "id": q["id"],
                        "choice_id": choice_id,
                        "initial": False
                    })
                    logger.info(f"Added evidence from answer: {q['id']} with choice {choice_id}")
                
                elif q.get("type") == "group_single":
                    # Handle group questions
                    for item in q.get("items", []):
                        if question_text in item.get("text", ""):
                            if str(answer).lower() in ["yes", "present"]:
                                choice_id = "present"
                            elif str(answer).lower() in ["no", "absent"]:
                                choice_id = "absent"
                            else:
                                choice_id = "unknown"
                            
                            state["evidence"].append({
                                "id": item["id"],
                                "choice_id": choice_id,
                                "initial": False
                            })
                            logger.info(f"Added evidence from group answer: {item['id']} with choice {choice_id}")
                            break
            
            # Clear the last question after processing
            state["last_question"] = None

        # If this is a new message and we have no evidence, try to extract symptoms
        elif user_message and not state["evidence"]:
            logger.info("New message - attempting to extract symptoms")
            
            # First try parsing
            parse_payload = {
                "text": user_message,
                "sex": state["sex"],
                "age": {"value": state["age"]}
            }
            
            logger.info(f"Sending parse request with payload: {parse_payload}")
            try:
                parse_resp = requests.post(
                    f"{INFERMEDICA_API_URL}/parse",
                    json=parse_payload,
                    headers=headers
                )
                parse_resp.raise_for_status()
                parse_json = parse_resp.json()
                logger.info(f"Parse response: {parse_json}")
                
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
                            logger.info(f"Added symptom from parse: {symptom_id} with choice {choice_id}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Error in parse request: {str(e)}")
            
            # If no symptoms found through parsing, try searching
            if not state["evidence"]:
                logger.info("No symptoms found through parsing, trying search")
                try:
                    search_resp = requests.get(
                        f"{INFERMEDICA_API_URL}/search",
                        params={"phrase": user_message, "sex": state["sex"], "age.value": state["age"]},
                        headers=headers
                    )
                    search_resp.raise_for_status()
                    search_results = search_resp.json()
                    logger.info(f"Search results: {search_results}")
                    
                    for result in search_results:
                        if result.get("type") == "symptom":
                            symptom_id = result["id"]
                            state["evidence"].append({
                                "id": symptom_id,
                                "choice_id": "present",
                                "initial": True
                            })
                            logger.info(f"Added symptom from search: {symptom_id}")
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error in search request: {str(e)}")

        # Deduplicate evidence
        unique_evidence = []
        seen_ids = set()
        for e in state["evidence"] + state["risk_factors"]:
            if e["id"] not in seen_ids:
                unique_evidence.append(e)
                seen_ids.add(e["id"])
        logger.info(f"Collected {len(unique_evidence)} unique evidence items")

        # If we have no evidence at all, return an error
        if not unique_evidence:
            logger.error("No evidence found after all attempts")
            return "I couldn't identify any symptoms in your message. Please try describing your symptoms in more detail."

        # Call Infermedica API for diagnosis
        diagnosis_payload = {
            "evidence": unique_evidence,
            "sex": state["sex"],
            "age": {"value": state["age"]}
        }
        
        logger.info(f"Sending diagnosis request with payload: {diagnosis_payload}")
        try:
            diag_resp = requests.post(
                f"{INFERMEDICA_API_URL}/diagnosis",
                json=diagnosis_payload,
                headers=headers
            )
            diag_resp.raise_for_status()
            diag_json = diag_resp.json()
            logger.info(f"Received diagnosis response: {diag_json}")
            
            # Check if we have a new question
            if diag_json.get("question"):
                q = diag_json["question"]
                
                # Check if this question has already been answered
                if q.get("id") not in state.get("answered_questions", set()):
                    # Add to answered questions to prevent loops
                    if "answered_questions" not in state:
                        state["answered_questions"] = set()
                    state["answered_questions"].add(q.get("id"))
                    state["last_question"] = q
                    logger.info(f"Added new question: {q.get('id')}")
                    
                    # Format the question for display
                    question_text = q["text"]
                    if q.get("type") == "single":
                        choices = [c["label"] for c in q.get("choices", [])]
                        question_text += f"\nOptions: {', '.join(choices)}"
                        q["items"] = [{
                            "text": q["text"],
                            "type": "single",
                            "choices": choices,
                            "id": q.get("id")
                        }]
                    elif q.get("type") == "group_single":
                        items = []
                        for item in q.get("items", []):
                            choices = [c["label"] for c in item.get("choices", [])]
                            items.append({
                                "text": item.get("text", ""),
                                "type": "single",
                                "choices": choices,
                                "id": item.get("id")
                            })
                        q["items"] = items
                    
                    # Store the formatted question in state
                    state["last_question"] = q
                    logger.info(f"Formatted question: {q}")
                    
                    # Return the question with proper structure
                    return {
                        "text": question_text,
                        "type": q.get("type", "single"),
                        "items": q.get("items", []),
                        "id": q.get("id")
                    }
                else:
                    # Skip already answered question, continue with diagnosis
                    logger.info(f"Skipping already answered question: {q.get('id')}")
            
            # If no more questions or question already answered, return the diagnosis
            if diag_json.get("conditions"):
                conditions = sorted(diag_json["conditions"], key=lambda x: x["probability"], reverse=True)
                diagnosis_text = "Based on your symptoms, here are the possible conditions:\n\n"
                for i, condition in enumerate(conditions[:5], 1):
                    diagnosis_text += f"{i}. **{condition['name']}** - {condition['probability']:.1%} probability\n"
                
                # Add emergency warning if present
                if diag_json.get("has_emergency_evidence"):
                    diagnosis_text += "\n⚠️ **URGENT**: Your symptoms may indicate a medical emergency. Please seek immediate medical care."
                
                # Add general medical advice
                diagnosis_text += "\n\n*Please consult with a healthcare professional for proper diagnosis and treatment.*"
                
                logger.info("Returning diagnosis with conditions")
                return diagnosis_text
            else:
                return "I couldn't determine a specific diagnosis based on the symptoms provided. Please consult with a healthcare professional for a proper evaluation."
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in diagnosis request: {str(e)}")
            return "I'm having trouble processing your symptoms right now. Please try again or consult with a healthcare professional."
            
    except Exception as e:
        logger.error(f"Error in infermedica_conversational_flow: {str(e)}", exc_info=True)
        return "An error occurred while processing your symptoms. Please try again or consult with a healthcare professional."
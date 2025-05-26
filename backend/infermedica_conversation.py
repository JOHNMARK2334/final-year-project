import requests
import os
import logging
import difflib

def get_infermedica_headers():
    app_id = os.getenv("INFERMEDICA_APP_ID")
    app_key = os.getenv("INFERMEDICA_APP_KEY")
    if not app_id or not app_key:
        logging.error("Infermedica API keys are not set. Please set INFERMEDICA_APP_ID and INFERMEDICA_APP_KEY in your environment.")
        return None
    return {
        "App-Id": app_id,
        "App-Key": app_key,
        "Content-Type": "application/json"
    }

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

def infermedica_conversational_flow(state, user_message, context=None, hide_default_openai_response=False, answers_dict=None, callback=None):
    headers = get_infermedica_headers()
    if not headers:
        return "Medical reasoning engine is not configured. Please contact the administrator."

    if context is None:
        context = []

    # Initialize state if empty
    if not state:
        state["evidence"] = []
        state["risk_factors"] = []
        state["sex"] = "male"
        state["age"] = 30
        state["step"] = "start"
        state["callback"] = callback  # Store callback in state

    # If last question exists and expects an answer, process it
    if state.get("last_question"):
        q = state["last_question"]
        answered_items = set()
        items = q.get("items", [])
        
        # Process answers based on callback type
        if callback == "process_symptoms":
            # Handle symptom-specific processing
            for item in items:
                if item.get("type") == "symptom":
                    for choice in item.get("choices", []):
                        if choice["label"].lower() in user_message.lower():
                            state["evidence"].append({"id": item["id"], "choice_id": choice["id"]})
                            answered_items.add(item["id"])
        elif callback == "process_risk_factors":
            # Handle risk factor-specific processing
            for item in items:
                if item.get("type") == "risk_factor":
                    for choice in item.get("choices", []):
                        if choice["label"].lower() in user_message.lower():
                            state["risk_factors"].append({"id": item["id"], "choice_id": choice["id"]})
                            answered_items.add(item["id"])
        else:
            # Default processing
            if answers_dict:
                if isinstance(answers_dict, str):
                    split_answers = [a.strip() for a in answers_dict.split(";")]
                    for idx, item in enumerate(items):
                        if idx < len(split_answers):
                            user_answer = split_answers[idx]
                            for choice in item.get("choices", []):
                                if choice["label"].lower() == user_answer.lower():
                                    state["evidence"].append({"id": item["id"], "choice_id": choice["id"]})
                                    answered_items.add(item["id"])
                elif isinstance(answers_dict, dict):
                    for item in items:
                        item_name = item.get("name", "")
                        user_answer = answers_dict.get(item_name)
                        if user_answer:
                            if isinstance(user_answer, list):
                                for ans in user_answer:
                                    for choice in item.get("choices", []):
                                        if choice["label"].lower() == str(ans).lower():
                                            state["evidence"].append({"id": item["id"], "choice_id": choice["id"]})
                                            answered_items.add(item["id"])
                            else:
                                for choice in item.get("choices", []):
                                    if choice["label"].lower() == str(user_answer).lower():
                                        state["evidence"].append({"id": item["id"], "choice_id": choice["id"]})
                                        answered_items.add(item["id"])
            else:
                # Try to answer from user_message first, then from context
                for item in items:
                    choice_labels = [choice["label"] for choice in item.get("choices", [])]
                    matched = fuzzy_match(user_message, choice_labels)
                    if not matched:
                        for prev in reversed(context):
                            matched = fuzzy_match(prev, choice_labels)
                            if matched:
                                break
                    if matched:
                        for choice in item.get("choices", []):
                            if choice["label"] == matched:
                                state["evidence"].append({"id": item["id"], "choice_id": choice["id"]})
                                answered_items.add(item["id"])
                                break

        # Only clear last_question if ALL items have been answered
        all_ids = {item["id"] for item in items}
        if answered_items == all_ids:
            state["last_question"] = None
            state["callback"] = None  # Clear callback after processing
        else:
            return q["text"]

    # --- Use v3 Parse API to extract symptoms/risk factors from user_message ---
    parse_result = parse_infermedica(user_message, state["sex"], state["age"])
    found = False
    if parse_result and "mentions" in parse_result:
        for mention in parse_result["mentions"]:
            mention_type = mention.get("type")
            if mention_type == "symptom":
                symp_id = mention["id"]
                if not any(e["id"] == symp_id for e in state["evidence"]):
                    state["evidence"].append({"id": symp_id, "choice_id": mention.get("choice_id", "present")})
                    found = True
            elif mention_type == "risk_factor":
                rf_id = mention["id"]
                if not any(rf["id"] == rf_id for rf in state["risk_factors"]):
                    state["risk_factors"].append({"id": rf_id, "choice_id": mention.get("choice_id", "present")})
                    found = True

    # --- Fallback: Use /search if parse didn't find anything ---
    if not found:
        search_results = search_infermedica(user_message, state["sex"], state["age"])
        for item in search_results:
            item_type = item.get("type")
            if item_type == "symptom":
                symp_id = item["id"]
                if not any(e["id"] == symp_id for e in state["evidence"]):
                    state["evidence"].append({"id": symp_id, "choice_id": "present"})
                    found = True
            elif item_type == "risk_factor":
                rf_id = item["id"]
                if not any(rf["id"] == rf_id for rf in state["risk_factors"]):
                    state["risk_factors"].append({"id": rf_id, "choice_id": "present"})
                    found = True

    # --- Optionally: Use v3 Get info API for additional info (not required for diagnosis, but can be logged or shown) ---
    info_result = get_info_infermedica(user_message, state["sex"], state["age"])
    # You can use info_result for further context or debugging if needed.

    # If nothing found and no evidence, ask for clarification
    if not found and not state["evidence"] and not state["risk_factors"]:
        return "I'm sorry, I couldn't identify any symptoms or risk factors in your message. Could you describe your symptoms in more detail?"

    # Call /diagnosis
    diagnosis_payload = {
        "sex": state["sex"],
        "age": {"value": state["age"]},
        "evidence": state["evidence"] + state["risk_factors"]
    }
    try:
        diag_resp = requests.post(
            "https://api.infermedica.com/v3/diagnosis",
            headers=headers,
            json=diagnosis_payload
        )
        diag_resp.raise_for_status()
        diag_json = diag_resp.json()
    except Exception:
        return "Sorry, there was a problem connecting to the medical reasoning engine. Please try again later."

    # If diagnosis returns a question, ask it
    if diag_json.get("question"):
        q = diag_json["question"]
        state["step"] = "question"
        state["last_question"] = q
        question_text = q["text"]
        choices = []
        for item in q.get("items", []):
            label = item.get("name", "")
            choice_labels = [c["label"] for c in item.get("choices", [])]
            choices.append(f"{label}: {', '.join(choice_labels)}")
        choices_str = "\n".join(choices)
        return f"{question_text}\n{choices_str}"

    # If diagnosis returns conditions, show them
    if diag_json.get("conditions"):
        state["step"] = "diagnosis"
        conditions = diag_json["conditions"]
        summary = "Based on your answers, possible conditions are:\n"
        for c in conditions[:5]:
            summary += f"- {c['common_name']} ({int(c['probability']*100)}%)\n"
        if diag_json.get("has_emergency_evidence"):
            summary += "\n⚠️ Your symptoms may indicate a medical emergency. Please seek immediate care."
        return summary

    return "Thank you for the information. If you have more symptoms, please describe them."
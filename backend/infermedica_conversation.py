import requests
import os
import logging

INFERMEDICA_APP_ID = os.getenv("INFERMEDICA_APP_ID")
INFERMEDICA_APP_KEY = os.getenv("INFERMEDICA_APP_KEY")

if not INFERMEDICA_APP_ID or not INFERMEDICA_APP_KEY:
    logging.error("Infermedica API keys are not set. Please set INFERMEDICA_APP_ID and INFERMEDICA_APP_KEY in your environment.")

HEADERS = {
    "App-Id": INFERMEDICA_APP_ID,
    "App-Key": INFERMEDICA_APP_KEY,
    "Content-Type": "application/json"
}

def get_info_infermedica(text, sex, age):
    """Infermedica v3 Get info API: extracts structured info from free text."""
    try:
        resp = requests.post(
            "https://api.infermedica.com/v3/info",
            headers=HEADERS,
            json={"text": text, "sex": sex, "age": {"value": age}}
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {}

def parse_infermedica(text, sex, age):
    """Infermedica v3 Parse API: parses symptoms and risk factors from free text."""
    try:
        resp = requests.post(
            "https://api.infermedica.com/v3/parse",
            headers=HEADERS,
            json={"text": text, "sex": sex, "age": {"value": age}}
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {}

def search_infermedica(phrase, sex, age):
    try:
        resp = requests.get(
            "https://api.infermedica.com/v3/search",
            headers=HEADERS,
            params={"phrase": phrase, "sex": sex, "age.value": age}
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return []

def get_symptom_details(symptom_id):
    try:
        resp = requests.get(
            f"https://api.infermedica.com/v3/symptoms/{symptom_id}",
            headers=HEADERS
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}

def get_risk_factor_details(risk_factor_id):
    try:
        resp = requests.get(
            f"https://api.infermedica.com/v3/risk_factors/{risk_factor_id}",
            headers=HEADERS
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}

def infermedica_conversational_flow(state, user_message):
    if not INFERMEDICA_APP_ID or not INFERMEDICA_APP_KEY:
        return "Medical reasoning engine is not configured. Please contact the administrator."

    # Initialize state if empty
    if not state:
        state["evidence"] = []
        state["risk_factors"] = []
        state["sex"] = "male"
        state["age"] = 30
        state["step"] = "start"

    # If last question exists and expects an answer, process it
    if state.get("last_question"):
        q = state["last_question"]
        for item in q.get("items", []):
            for choice in item.get("choices", []):
                if choice["label"].lower() in user_message.lower():
                    state["evidence"].append({"id": item["id"], "choice_id": choice["id"]})
        state["last_question"] = None

    # --- Use v3 Parse API to extract symptoms/risk factors from user_message ---
    parse_result = parse_infermedica(user_message, state["sex"], state["age"])
    found = False
    if parse_result and "mentions" in parse_result:
        for mention in parse_result["mentions"]:
            if mention["type"] == "symptom":
                symp_id = mention["id"]
                if not any(e["id"] == symp_id for e in state["evidence"]):
                    state["evidence"].append({"id": symp_id, "choice_id": mention.get("choice_id", "present")})
                    found = True
            elif mention["type"] == "risk_factor":
                rf_id = mention["id"]
                if not any(rf["id"] == rf_id for rf in state["risk_factors"]):
                    state["risk_factors"].append({"id": rf_id, "choice_id": mention.get("choice_id", "present")})
                    found = True

    # --- Fallback: Use /search if parse didn't find anything ---
    if not found:
        search_results = search_infermedica(user_message, state["sex"], state["age"])
        for item in search_results:
            if item["type"] == "symptom":
                symp_id = item["id"]
                if not any(e["id"] == symp_id for e in state["evidence"]):
                    state["evidence"].append({"id": symp_id, "choice_id": "present"})
                    found = True
            elif item["type"] == "risk_factor":
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
            headers=HEADERS,
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
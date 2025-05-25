import requests

def get_diagnosis(symptoms_text, sex="male", age=30, symptoms=None):
    headers = {
        'App-Id': '664abe91',  # Replace with your Infermedica App-Id
        'App-Key': '31cfbbb9c19870b80dce490572a6ddb9',  # Replace with your Infermedica App-Key
        'Content-Type': 'application/json'
    }
    # Step 1: Parse symptoms from text and explicit symptoms
    parse_data = {
        "text": symptoms_text,
        "sex": sex,
        "age": {"value": age}
    }
    parse_response = requests.post("https://api.infermedica.com/v3/parse", headers=headers, json=parse_data)
    parse_json = parse_response.json()
    evidence = []
    for mention in parse_json.get("mentions", []):
        evidence.append({
            "id": mention["id"],
            "choice_id": mention["choice_id"]
        })
    # Add explicit symptoms if provided (implement mapping if needed)
    # for s in symptoms: ... (optional)
    if not evidence:
        return {"conditions": []}
    diagnosis_data = {
        "sex": sex,
        "age": {"value": age},
        "evidence": evidence
    }
    diagnosis_response = requests.post("https://api.infermedica.com/v3/diagnosis", headers=headers, json=diagnosis_data)
    return diagnosis_response.json()

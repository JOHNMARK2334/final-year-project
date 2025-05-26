import streamlit as st
import pandas as pd
import requests

def get_symptom_ids(symptom_text, headers):
    symptoms = []
    # Replace " and " and " or " with commas, then split
    phrases = [phrase.strip() for phrase in symptom_text.lower().replace(" and ", ",").replace(" or ", ",").split(",")]

    # Get age value from session state (ensure it's set and valid)
    try:
        age_value = int(st.session_state.form_data.get("Age", 0))
    except Exception:
        age_value = 0

    for phrase in phrases:
        if not phrase:
            continue  # Skip empty phrases

        st.write(f"🔍 Searching Infermedica for: '{phrase}'")

        try:
            response = requests.get(
                "https://api.infermedica.com/v3/search",
                headers=headers,
                params={
                    "phrase": phrase,
                    "types": "symptom",
                    "age.value": age_value
                }
            )
            print("Requesting:", response.url)
            print("Status code:", response.status_code)
            print("Response text:", response.text)

            if response.status_code == 200:
                results = response.json()
                if results:
                    st.write(f"✅ Found: {results[0]['label']} → {results[0]['id']}")
                    symptoms.append({"id": results[0]["id"], "choice_id": "present"})
                else:
                    st.warning(f"⚠️ No results for '{phrase}'")
            else:
                st.error(f"❌ Error from API: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Exception searching '{phrase}': {str(e)}")

    return symptoms

def main():
    st.title("Medical Diagnosis Wizard")

    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0

    if 'completed' not in st.session_state:
        st.session_state.completed = []

    if 'form_data' not in st.session_state:
        st.session_state.form_data = {
            "Age": "",
            "Gender": "",
            "Height": "",
            "Weight": "",
            "Primary Symptom": "",
            "Symptom Duration": "",
            "Symptom Severity": "Moderate",
            "Existing Conditions": "",
            "Current Medications": "",
            "Allergies": ""
        }

    steps = [
        {"title": "Basic Information", "fields": ["Age", "Gender", "Height", "Weight"]},
        {"title": "Main Symptoms", "fields": ["Primary Symptom", "Symptom Duration", "Symptom Severity"]},
        {"title": "Medical History", "fields": ["Existing Conditions", "Current Medications", "Allergies"]},
        {"title": "Review & Results", "fields": []}
    ]

    st.progress(st.session_state.current_step / (len(steps) - 1))

    cols = st.columns(len(steps))
    for i, step in enumerate(steps):
        with cols[i]:
            bg = "#4CAF50" if i < st.session_state.current_step else "#1E88E5" if i == st.session_state.current_step else "#E0E0E0"
            color = "white" if i <= st.session_state.current_step else "#757575"
            label = "✓" if i < st.session_state.current_step else str(i + 1)
            st.markdown(
                f"""
                <div style='text-align: center;'>
                    <div style='width: 30px; height: 30px; border-radius: 50%; background: {bg}; color: {color}; display: inline-flex; align-items: center; justify-content: center; font-weight: bold;'>{label}</div>
                    <p style='color: {color}; font-size: 14px; margin-top: 5px;'>{step['title']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.header(steps[st.session_state.current_step]["title"])

    def go_to_next():
        current_fields = steps[st.session_state.current_step]["fields"]
        is_complete = all(st.session_state.form_data[field] != "" for field in current_fields)
        if is_complete:
            if st.session_state.current_step not in st.session_state.completed:
                st.session_state.completed.append(st.session_state.current_step)
            st.session_state.current_step += 1
        else:
            st.error("Please fill in all fields before proceeding.")

    def go_to_previous():
        st.session_state.current_step -= 1

    if st.session_state.current_step < 3:
        for field in steps[st.session_state.current_step]["fields"]:
            if field == "Gender":
                st.session_state.form_data[field] = st.selectbox(
                    field,
                    options=["", "Male", "Female"],
                    index=["", "Male", "Female"].index(st.session_state.form_data[field]) if st.session_state.form_data[field] else 0
                )
            elif field == "Symptom Severity":
                st.session_state.form_data[field] = st.select_slider(
                    field,
                    options=["Mild", "Moderate", "Severe", "Very Severe"],
                    value=st.session_state.form_data[field]
                )
            else:
                st.session_state.form_data[field] = st.text_input(field, value=st.session_state.form_data[field])
    else:
        st.subheader("Summary of Information")
        for i, step in enumerate(steps[:3]):
            st.markdown(f"#### {step['title']}")
            data = {field: [st.session_state.form_data[field]] for field in step["fields"]}
            df = pd.DataFrame(data)
            st.dataframe(df)

        st.subheader("Assessment Results")
        st.markdown("#### Potential Conditions (powered by Infermedica)")

        headers = {
            "App-Id": st.secrets["INFERMEDICA_APP_ID"] if "INFERMEDICA_APP_ID" in st.secrets else None,
            "App-Key": st.secrets["INFERMEDICA_APP_KEY"] if "INFERMEDICA_APP_KEY" in st.secrets else None,
            "Content-Type": "application/json"
        }
        if not headers["App-Id"] or not headers["App-Key"]:
            st.warning("Infermedica API keys are not set in Streamlit secrets. Please add them to .streamlit/secrets.toml.")
        # Ensure gender is either 'male' or 'female'
        gender = st.session_state.form_data["Gender"].lower()
        if gender not in ["male", "female"]:
            gender = "male"
        evidence = get_symptom_ids(st.session_state.form_data["Primary Symptom"], headers)

        if not evidence:
            st.warning("""❌ No valid symptoms found.
Try entering more common terms like: 'headache', 'fever', 'fatigue', or 'nausea'.""")
        else:
            payload = {
                "sex": gender,
                "age": {"value": int(st.session_state.form_data["Age"])},
                "evidence": evidence
            }

            st.markdown("##### 🔍 Final Diagnostic Payload:")
            st.json(payload)
            st.markdown("##### 🔍 Headers:")
            st.json(headers)

            try:
                response = requests.post("https://api.infermedica.com/v3/diagnosis", json=payload, headers=headers)
                st.markdown("##### 🔍 API Response:")
                st.json(response.json())

                if response.status_code == 200:
                    conditions = response.json().get("conditions", [])
                    for i, condition in enumerate(conditions[:5]):
                        st.markdown(f"**{i+1}. {condition['name']}** - Probability: {round(condition['probability']*100, 2)}%")
                else:
                    st.error("Failed to retrieve diagnosis from Infermedica API")
            except Exception as e:
                st.error(f"Error connecting to Infermedica API: {str(e)}")

        st.info("Note: These results are not a medical diagnosis and should not replace professional medical consultation.")

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.current_step > 0:
            st.button("← Previous", on_click=go_to_previous, key="prev_button", use_container_width=True)
    with col2:
        if st.session_state.current_step < len(steps) - 1:
            st.button("Next →", on_click=go_to_next, key="next_button", type="primary", use_container_width=True)
        else:
            if st.button("Finish", key="finish_button", type="primary", use_container_width=True):
                st.balloons()
                st.success("Your diagnosis has been submitted successfully!")

if __name__ == "__main__":
    main()

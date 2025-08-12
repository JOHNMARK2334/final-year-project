import streamlit as st
import pandas as pd
import requests

def get_symptom_ids(symptom_text, headers, age_value_str):
    symptoms = []
    phrases = [phrase.strip() for phrase in symptom_text.lower().replace(" and ", ",").replace(" or ", ",").split(",")]

    try:
        age_value = int(age_value_str)
    except ValueError:
        st.error("Invalid age format provided for symptom search.")
        return []

    for phrase in phrases:
        if not phrase:
            continue
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
            if response.status_code == 200:
                results = response.json()
                if results:
                    symptoms.append({"id": results[0]["id"], "choice_id": "present"})
            else:
                st.error(f"❌ Error searching for symptom '{phrase}': {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Exception searching '{phrase}': {str(e)}")
    return symptoms

# Modified render signature: Removed auth_token and on_logout_callback
def render(backend_url=None, on_navigate=None):
    
    headers = {
        "App-Id": st.secrets.get("INFERMEDICA_APP_ID"),
        "App-Key": st.secrets.get("INFERMEDICA_APP_KEY"),
        "Content-Type": "application/json"
    }
    
    # Removed is_user_logged_in from main's call
    main(headers=headers, on_navigate_callback=on_navigate)

# Modified main signature: Removed is_user_logged_in
def main(headers=None, on_navigate_callback=None):
    st.title("Medical Diagnosis Wizard")

    default_form_data = {
        "Age": "", "Gender": "", "Height": "", "Weight": "",
        "Primary Symptom": "", "Symptom Duration": "", "Symptom Severity": "Moderate",
        "Existing Conditions": "", "Current Medications": "", "Allergies": ""
    }

    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'completed' not in st.session_state:
        st.session_state.completed = []
    if 'form_data' not in st.session_state:
        st.session_state.form_data = default_form_data.copy()

    steps = [
        {"title": "Basic Information", "fields": ["Age", "Gender", "Height", "Weight"]},
        {"title": "Main Symptoms", "fields": ["Primary Symptom", "Symptom Duration", "Symptom Severity"]},
        {"title": "Medical History", "fields": ["Existing Conditions", "Current Medications", "Allergies"]},
        {"title": "Review & Results", "fields": []}
    ]

    st.progress(st.session_state.current_step / (len(steps) - 1))

    cols_steps = st.columns(len(steps))
    for i, step in enumerate(steps):
        with cols_steps[i]:
            bg = "#4CAF50" if i < st.session_state.current_step else "#1E88E5" if i == st.session_state.current_step else "#E0E0E0"
            color = "white" if i <= st.session_state.current_step else "#757575"
            label = "✓" if i < st.session_state.current_step else str(i + 1)
            st.markdown(
                f"""
                <div style='text-align: center;'>
                    <div style='width: 30px; height: 30px; border-radius: 50%; background: {bg}; color: {color}; display: inline-flex; align-items: center; justify-content: center; font-weight: bold;'>{label}</div>
                    <p style='color: {color}; font-size: 14px; margin-top: 5px;'>{step["title"]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.header(steps[st.session_state.current_step]["title"])

    def reset_wizard():
        st.session_state.current_step = 0
        st.session_state.form_data = default_form_data.copy()
        st.session_state.completed = []
        # No explicit navigation here, just reset state and rerun
        # If on_navigate_callback is to be used to go to a specific page after reset,
        # it would be called here, e.g., on_navigate_callback('wizard') or on_navigate_callback('home')

    def go_to_next():
        current_fields = steps[st.session_state.current_step]["fields"]
        is_complete = all(st.session_state.form_data.get(field, "") != "" for field in current_fields)
        if is_complete:
            if st.session_state.current_step not in st.session_state.completed:
                st.session_state.completed.append(st.session_state.current_step)
            st.session_state.current_step += 1
        else:
            st.error("Please fill in all fields before proceeding.")

    def go_to_previous():
        st.session_state.current_step -= 1

    if st.session_state.current_step < 3: # Form steps
        for field in steps[st.session_state.current_step]["fields"]:
            if field == "Gender":
                st.session_state.form_data[field] = st.selectbox(
                    field, options=["", "Male", "Female"],
                    index=["", "Male", "Female"].index(st.session_state.form_data.get(field, ""))
                )
            elif field == "Symptom Severity":
                st.session_state.form_data[field] = st.select_slider(
                    field, options=["Mild", "Moderate", "Severe", "Very Severe"],
                    value=st.session_state.form_data.get(field, "Moderate")
                )
            else:
                st.session_state.form_data[field] = st.text_input(field, value=st.session_state.form_data.get(field, ""))
    else: # Review & Results step
        st.subheader("Summary of Information")
        for i, step_info in enumerate(steps[:3]):
            st.markdown(f"#### {step_info['title']}")
            data_summary = {field: [st.session_state.form_data.get(field,"N/A")] for field in step_info["fields"]}
            df = pd.DataFrame(data_summary)
            st.dataframe(df)

        st.subheader("Assessment Results")

        if not headers.get("App-Id") or not headers.get("App-Key"):
            st.warning("Diagnosis feature is currently unavailable due to configuration issues. Please contact support.")
        else:
            st.markdown("#### Potential Conditions (powered by Infermedica)")
            
            gender = st.session_state.form_data.get("Gender", "").lower()
            age_str = st.session_state.form_data.get("Age", "")

            if gender not in ["male", "female"]:
                st.error("Invalid or missing gender. Please go back and select Male or Female.")
                return 
            try:
                age_value = int(age_str)
                if age_value <= 0 or age_value > 120: 
                    st.error("Invalid or missing age. Please go back and enter a valid age (1-120).")
                    return
            except ValueError:
                st.error("Invalid or missing age format. Please go back and enter a numeric age.")
                return

            primary_symptom_text = st.session_state.form_data.get("Primary Symptom", "")
            if not primary_symptom_text.strip():
                st.warning("Primary symptom is missing. Please go back and enter your main symptom.")
                return

            evidence = get_symptom_ids(primary_symptom_text, headers, age_str)

            if not evidence:
                st.warning("No valid symptoms found based on your input. Try rephrasing or using common medical terms like 'headache', 'fever', etc.")
            else:
                payload = {
                    "sex": gender,
                    "age": {"value": age_value},
                    "evidence": evidence
                }
                try:
                    response = requests.post("https://api.infermedica.com/v3/diagnosis", json=payload, headers=headers)
                    if response.status_code == 200:
                        conditions = response.json().get("conditions", [])
                        if conditions:
                            for i, condition in enumerate(conditions[:5]): 
                                st.markdown(f"**{i+1}. {condition['name']}** - Probability: {round(condition['probability']*100, 2)}%")
                        else:
                            st.info("No specific conditions were identified based on the provided symptoms.")
                    else:
                        st.error(f"Failed to retrieve diagnosis from Infermedica API: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Error connecting to Infermedica API: {str(e)}")
        
        st.info("Note: These results are not a medical diagnosis and should not replace professional medical consultation.")

    col1_nav, col2_nav = st.columns(2)
    with col1_nav:
        if st.session_state.current_step > 0:
            st.button("← Previous", on_click=go_to_previous, key="prev_button", use_container_width=True)
    with col2_nav:
        if st.session_state.current_step < len(steps) - 1:
            st.button("Next →", on_click=go_to_next, key="next_button", type="primary", use_container_width=True)
        else: 
            if st.button("Finish", key="finish_button", type="primary", use_container_width=True):
                st.balloons()
                st.success("Thank you for using the Diagnosis Wizard!")
                # Reset the wizard state
                reset_wizard()
                # Rerun to reflect the reset state (e.g., go back to step 0)
                st.rerun()

if __name__ == "__main__":
    main(headers={"App-Id": "test", "App-Key": "test"})

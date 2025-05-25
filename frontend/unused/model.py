import streamlit as st
import requests

st.title("💬 AI Medical Consultation")

option = st.radio("Choose input method:", ("Text", "Voice", "Image"))

if option == "Text":
    user_input = st.text_area("Describe your symptoms:")
    if st.button("Submit"):
        response = requests.post("http://localhost:5000/api/query", json={"text": user_input})
        data = response.json()
        st.subheader("Infermedica Response")
        st.json(data['infermedica'])
        st.subheader("AI Response")
        st.write(data['openai'])

elif option == "Voice":
    audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3"])
    if audio_file:
        response = requests.post("http://localhost:5000/api/audio", files={"audio": audio_file})
        transcribed = response.json()
        st.subheader("Transcribed Text")
        st.write(transcribed['text'])

elif option == "Image":
    img_file = st.file_uploader("Upload an image", type=["jpg", "png"])
    if img_file:
        response = requests.post("http://localhost:5000/api/image", files={"image": img_file})
        caption = response.json()
        st.subheader("Image Caption")
        st.write(caption['caption'])

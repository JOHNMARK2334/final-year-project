from streamlit_realtime_audio_recorder import audio_recorder
import streamlit as st
import base64
import io

result = audio_recorder(
    interval=50,
    threshold=-60,
    silenceTimeout=200
)

if result:
    if result.get('status') == 'stopped':
        audio_data = result.get('audioData')
        if audio_data:
            audio_bytes = base64.b64decode(audio_data)
            audio_file = io.BytesIO(audio_bytes)
            st.audio(audio_file, format="audio/webm")
        else:
            pass
    elif result.get('error'):
            st.error(f"Error: {result.get('error')}")
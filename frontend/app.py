import streamlit as st
import os
import sys
from dotenv import load_dotenv
import requests
import components.navigation as navigation
import pages.home_page as home_page
import pages.chat_page as chat_page
import pages.diagnosis_wizard as diagnosis_wizard
import pages.auth_page as auth_page
from datetime import datetime

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
BACKEND_URL = "http://127.0.0.1:5000/api"

# Configure the Streamlit page
st.set_page_config(
    page_title="HealthAssist",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

def set_page(page_name):
    st.session_state.current_page = page_name

def login(username, password):
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.auth_token = data['access_token']
            st.session_state.user_info = {
                'user_id': data['user_id'],
                'username': data['username']
            }
            st.success("Login successful!")
            st.write("Token:", st.session_state.auth_token)
            set_page('home')
            st.rerun()  # Optionally rerun to update UI
            return True
        else:
            st.error(response.json().get('error', 'Login failed'))
            return False
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return False

def register(username, password, email):
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json={"username": username, "password": password, "email": email},
            timeout=5
        )
        if response.status_code == 201:
            st.success("Registration successful! Please login.")
            set_page('login')
            return True
        else:
            st.error(response.json().get('error', 'Registration failed'))
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to backend. Is it running? Error: {str(e)}")
        return False

def logout():
    st.session_state.auth_token = None
    st.session_state.user_info = None
    set_page('login')

# Main app logic
if st.session_state.auth_token and st.session_state.user_info:
    st.write(f"Welcome, {st.session_state.user_info['username']}!")
    
    # Show navigation only for home and chat pages
    if st.session_state.current_page in ['home', 'chat']:
        navigation.render(
            on_navigate=set_page,
            current_page=st.session_state.current_page,
            on_logout=logout
        )
    
    if st.session_state.current_page == 'home':
        home_page.render(lambda: set_page('chat'))
    elif st.session_state.current_page == 'chat':
        chat_page.render(
            backend_url=BACKEND_URL,
            on_start_diagnosis=lambda: set_page('wizard'),
            auth_token=st.session_state.auth_token
        )
    elif st.session_state.current_page == 'wizard':
        diagnosis_wizard.render(
            backend_url=BACKEND_URL,
            auth_token=st.session_state.auth_token,
            on_navigate=set_page
        )
    else:
        home_page.render(lambda: set_page('chat'))
else:
    auth_page.render(login, register)
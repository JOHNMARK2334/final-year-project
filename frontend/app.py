import streamlit as st
import os
import sys
from dotenv import load_dotenv
import requests
import components.navigation as navigation
import used.home_page as home_page
import used.chat_page as chat_page
import used.diagnosis_wizard as diagnosis_wizard
import used.auth_page as auth_page
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
            set_page('chat')  # Redirect to chat page after login
            st.rerun()
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
            st.success("Registration successful! Please login to continue.") # Message updated for clarity
            # Attempt to log in the user automatically after registration
            # This assumes the login function handles setting auth_token and user_info
            if login(username, password): # This will call set_page('chat') and rerun on success
                return True # login() already handles rerun
            else:
                # If auto-login fails, send them to the login page as before
                set_page('login')
                st.rerun()
                return False # Indicate registration was successful but login failed
        else:
            st.error(response.json().get('error', 'Registration failed'))
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to backend. Is it running? Error: {str(e)}")
        return False

def logout():
    st.session_state.auth_token = None
    st.session_state.user_info = None
    set_page('home')  # Redirect to home page after logout
    st.rerun()

# Main app logic
is_logged_in = bool(st.session_state.auth_token and st.session_state.user_info)
current_page = st.session_state.current_page

PAGES_REQUIRING_AUTH = ['chat'] # Removed 'wizard'

if current_page in PAGES_REQUIRING_AUTH and not is_logged_in:
    st.info("Please log in to access this page.")
    auth_page.render(login, register) # Show login/register page
elif current_page == 'login' or current_page == 'register': # Explicit navigation to auth pages
    auth_page.render(login, register)
else:
    navigation.render(
        on_navigate=set_page,
        current_page=current_page,
        is_logged_in=is_logged_in,  # Pass the login status
        on_logout=logout
    )

    if current_page == 'home':
        # The lambda set_page('chat') will trigger the auth check if user is not logged in
        home_page.render(on_start_checkup=lambda: set_page('chat'))
    elif current_page == 'chat': # This block is reached only if is_logged_in is True for 'chat'
        chat_page.render(auth_token=st.session_state.auth_token)
    elif current_page == 'wizard': 
        diagnosis_wizard.render(
            backend_url=BACKEND_URL, 
            on_navigate=set_page
        )
    # else: # Fallback for any unexpected page state
    #     set_page('home')
    #     st.rerun()
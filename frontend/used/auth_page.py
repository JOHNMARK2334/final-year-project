import streamlit as st

def render(login_callback, register_callback):
    st.markdown(
        """
        <style>
            .main {
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 80vh; /* Use min-height to ensure it takes up space */
            }
            .auth-container {
                width: 100%;
                max-width: 400px; /* Max width for the form container */
                padding: 15px 30px 30px 30px; /* MODIFIED: Reduced top padding */
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                background-color: white;
            }
            /* ADDED: Target header (typically h2) within auth-container to remove its top margin */
            .auth-container h2 { 
                margin-top: 0px !important; 
            }
            .stButton>button {
                width: 100%; /* Make Streamlit buttons full width */
            }
            .toggle-button-container {
                margin-top: 20px;
                text-align: center;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    if 'auth_form_to_display' not in st.session_state:
        st.session_state.auth_form_to_display = 'login' # Default to login form

    st.markdown('<div class="auth-container">', unsafe_allow_html=True)

    if st.session_state.auth_form_to_display == 'login':
        st.header("Login to HealthAssist")
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submit_login = st.form_submit_button("Login")

            if submit_login:
                if login_callback(username, password):
                    # Callbacks should handle page redirection via session_state.page and st.rerun()
                    pass # Assuming login_callback handles success and rerun
        
        st.markdown('<div class="toggle-button-container">', unsafe_allow_html=True)
        if st.button("Don't have an account? Sign Up", key="goto_register"):
            st.session_state.auth_form_to_display = 'register'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.auth_form_to_display == 'register':
        st.header("Create an Account")
        with st.form("register_form"):
            username = st.text_input("Username", key="register_username")
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_password")
            submit_register = st.form_submit_button("Register")

            if submit_register:
                if password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    if register_callback(username, password, email):
                        # Callbacks should handle page redirection via session_state.page and st.rerun()
                        pass # Assuming register_callback handles success and rerun

        st.markdown('<div class="toggle-button-container">', unsafe_allow_html=True)
        if st.button("Already have an account? Login", key="goto_login"):
            st.session_state.auth_form_to_display = 'login'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True) # Close auth-container
import streamlit as st

def render(login_callback, register_callback):
    st.markdown(
        """
        <style>
            .main {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 80vh;
            }
            .auth-container {
                width: 400px;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                background-color: white;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        with st.form("login_form"):
            st.header("Login to HealthAssist")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                if login_callback(username, password):
                    st.session_state.page = "chat"
                    st.rerun()

    with tab2:
        with st.form("register_form"):
            st.header("Create an Account")
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Register")

            if submit:
                if password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    if register_callback(username, password, email):
                        st.session_state.page = "chat"
                        st.rerun()
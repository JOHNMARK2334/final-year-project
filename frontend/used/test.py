import streamlit as st

def render(auth_token=None):
    """
    Minimal render function for testing
    """
    st.title("Chat Page - Test Version")
    st.write("This is a test version of the chat page.")
    st.write(f"Auth token received: {'Yes' if auth_token else 'No'}")
    
    if st.button("Test Button"):
        st.success("Chat page render function is working!")

# Test print to verify module loading
print("chat_page.py module loaded successfully with render function")
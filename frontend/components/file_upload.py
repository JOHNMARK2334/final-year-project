import streamlit as st

def render():
    """
    Renders a file upload button and returns the uploaded files
    
    Returns:
        list: List of uploaded files
    """
    uploaded_files = st.file_uploader(
        "Upload images or documents", 
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg", "pdf", "doc", "docx"],
        label_visibility="collapsed"
    )
    
    return uploaded_files

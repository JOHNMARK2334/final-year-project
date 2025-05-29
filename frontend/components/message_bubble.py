import streamlit as st
import base64
from PIL import Image
import io

def render(message):
    """
    Renders a message bubble with content and optional files
    
    Args:
        message: Dictionary containing message data (type, content, files)
    """
    is_user = message.get('type') == 'user'
    content = message.get('content', '')
    files = message.get('files', [])
    
    if is_user:
        # User message - right aligned
        container = st.container()
        with container:
            # Message content in a blue bubble
            st.markdown(
                f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                    <div style="max-width: 80%; padding: 10px 15px; border-radius: 15px; 
                         background-color: #1E88E5; color: white;">
                        {content}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Display files if any
            if files:
                cols = st.columns(min(len(files), 3))
                for idx, file in enumerate(files):
                    with cols[idx % min(len(files), 3)]:
                        if file.get('isImage', False):
                            st.image(file.get('data', None) or "https://via.placeholder.com/100", 
                                     caption=file.get('name', 'Image'), width=100)
                        else:
                            st.markdown(
                                f"""
                                <div style="display: flex; align-items: center; background-color: #1565C0; 
                                     color: white; padding: 5px; border-radius: 5px; margin-bottom: 5px;">
                                    <div style="height: 24px; width: 24px; margin-right: 8px; 
                                         background-color: #0D47A1; border-radius: 5px; 
                                         display: flex; align-items: center; justify-content: center;">
                                        Doc
                                    </div>
                                    <span style="white-space: nowrap; overflow: hidden; 
                                         text-overflow: ellipsis; max-width: 200px;">
                                        {file.get('name', 'Document')}
                                    </span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
    else:
        # Bot message - left aligned
        container = st.container()
        with container:
            # Message content in a white bubble
            st.markdown(
                f"""
                <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
                    <div style="max-width: 80%; padding: 10px 15px; border-radius: 15px; 
                         background-color: white; color: #333; border: 1px solid #E0E0E0;">
                        {content}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

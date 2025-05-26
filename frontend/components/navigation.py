import streamlit as st

def render(on_navigate, current_page, on_logout=None):  # Make on_logout optional
    col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
    
    with col1:
        st.markdown(
            f"""<div style="display: flex; align-items: center;">
                <span style="color: #1E88E5; font-weight: bold; font-size: 24px;">
                    HealthAssist
                </span>
            </div>""",
            unsafe_allow_html=True
        )
    
    with col2:
        col_home, col_symptom, _ = st.columns([1, 2, 3])
        
        with col_home:
            st.button('Home', 
                     key='nav_home', 
                     on_click=lambda: on_navigate('home'),
                     use_container_width=True)
        
        with col_symptom:
            st.button('Symptom Checker',
                     key='nav_chat',
                     on_click=lambda: on_navigate('chat'),
                     use_container_width=True)
    
    with col3:
        st.button('Start Checkup',
                 key='nav_checkup',
                 on_click=lambda: on_navigate('chat'),
                 use_container_width=True)
    
    if on_logout:  # Only show logout if callback provided
        with col4:
            st.button('Logout',
                     key='nav_logout',
                     on_click=on_logout,
                     use_container_width=True)
    
    st.markdown('<hr style="margin-top: 0px; margin-bottom: 15px;">', unsafe_allow_html=True)
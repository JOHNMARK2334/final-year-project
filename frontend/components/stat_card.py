import streamlit as st

def render(icon, value, label):
    """
    Renders a statistics card with icon, value and label
    
    Args:
        icon: Icon HTML or emoji to display
        value: Value to display
        label: Label to display
    """
    st.markdown(
        f"""
        <div style="background-color: #1565C0; border-radius: 10px; padding: 20px; text-align: center;">
            <div style="font-size: 32px; color: white;">{icon}</div>
            <p style="margin-top: 15px; font-size: 36px; font-weight: 800; color: white;">{value}</p>
            <p style="margin-top: 5px; font-size: 18px; font-weight: 600; color: #90CAF9;">{label}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

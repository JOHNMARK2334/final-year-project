import streamlit as st

def main():
    # Hide Streamlit sidebar and hamburger menu
    st.markdown("""
        <style>
        [data-testid=\"stSidebar\"], .css-1lcbmhc.e1fqkh3o3 { display: none !important; }
        [data-testid=\"collapsedControl\"] { display: none !important; }
        section[data-testid=\"stSidebarNav\"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)
    st.write(st.__version__)
    st.write(st.__file__)

if __name__ == "__main__":
    main()

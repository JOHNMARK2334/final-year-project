import streamlit as st

def render(on_navigate, current_page, is_logged_in, on_logout=None):
    nav_items = []

    # Define buttons based on state
    if is_logged_in:
        # Home button is always added
        nav_items.append({'label': 'Home', 'key': 'nav_home_loggedin', 'action': lambda: on_navigate('home')})

        if current_page == 'home':
            nav_items.append({'label': 'Symptom Checker', 'key': 'nav_sc_home_loggedin', 'action': lambda: on_navigate('wizard')})
            nav_items.append({'label': 'Start Checkup', 'key': 'nav_su_home_loggedin', 'action': lambda: on_navigate('chat')})
        elif current_page == 'wizard':  # On Symptom Checker page
            # Always show Start Checkup when on wizard page and logged in
            nav_items.append({'label': 'Start Checkup', 'key': 'nav_su_wizard_loggedin', 'action': lambda: on_navigate('chat')})
        elif current_page == 'chat':  # On Start Checkup page (Chat page)
            nav_items.append({'label': 'Symptom Checker', 'key': 'nav_sc_chat_loggedin', 'action': lambda: on_navigate('wizard')})
        # Logout button is handled separately
    else:  # Not logged in
        # Always show Home button
        nav_items.append({'label': 'Home', 'key': 'nav_home_loggedout', 'action': lambda: on_navigate('home')})

        if current_page == 'home':
            nav_items.append({'label': 'Symptom Checker', 'key': 'nav_sc_home_loggedout', 'action': lambda: on_navigate('wizard')})
            nav_items.append({'label': 'Start Checkup', 'key': 'nav_su_home_loggedout', 'action': lambda: on_navigate('chat')})
        elif current_page == 'wizard': # On Symptom Checker page (wizard)
            # Always show Start Checkup when on wizard page and logged out
            nav_items.append({'label': 'Start Checkup', 'key': 'nav_su_wizard_loggedout', 'action': lambda: on_navigate('chat')})
        # No Login/Register button in the navbar for other pages when logged out.
        # app.py handles redirection to auth_page if needed.

    num_main_buttons = len(nav_items)
    
    # Determine column ratios: Logo, then main buttons, then Logout if applicable
    column_ratios = [1.5]  # For logo
    if num_main_buttons > 0:
        column_ratios.extend([1] * num_main_buttons)
    if is_logged_in and on_logout:
        column_ratios.append(1)  # For logout button

    # Ensure there's at least one column for the logo if all else is absent
    if not column_ratios: # Should not be hit if logo is always [1.5]
        cols = st.columns([1])
    else:
        cols = st.columns(column_ratios)

    # Render Logo
    with cols[0]:
        st.markdown(
            f"""<div style="display: flex; align-items: center; height: 100%;">
                <span style="color: #1E88E5; font-weight: bold; font-size: 24px;">
                    HealthAssist
                </span>
            </div>""",
            unsafe_allow_html=True
        )

    # Render main navigation buttons
    for i, item in enumerate(nav_items):
        # Buttons start from cols[1]
        with cols[1 + i]:
            st.button(item['label'], key=item['key'], on_click=item['action'], use_container_width=True)

    # Render Logout button in the last designated column if logged in
    if is_logged_in and on_logout:
        logout_col_index = 1 + num_main_buttons
        if logout_col_index < len(cols): # Check if column exists
            with cols[logout_col_index]:
                st.button('Logout', key='nav_logout', on_click=on_logout, use_container_width=True)
    
    st.markdown('<hr style="margin-top: 0px; margin-bottom: 15px;">', unsafe_allow_html=True)
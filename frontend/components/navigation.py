import streamlit as st

def render(on_navigate, current_page, on_logout=None, show_checkup=True, show_symptom=True, key_suffix=None):
    if key_suffix is None:
        raise ValueError("A unique key_suffix must be provided to navigation.render() for widget key uniqueness.")
    
    # Determine which buttons to show based on page context
    # By default, show all buttons unless overridden
    show_home = True
    show_symptom_btn = show_symptom
    show_checkup_btn = show_checkup
    show_logout = False

    # Only show logout on chat page
    if current_page == 'chat':
        show_logout = True
        show_home = True
        show_symptom_btn = True
        show_checkup_btn = False
    # On diagnosis_wizard, only show home and start checkup
    elif current_page == 'wizard':
        show_logout = False
        show_home = True
        show_symptom_btn = False
        show_checkup_btn = True
    # On other pages, default logic (no logout)
    else:
        show_logout = False

    # Enhanced CSS with responsive design and uniform styling
    st.markdown("""
        <style>
        /* Global Navigation Styles */
        .navbar-container {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            width: 100%;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            z-index: 1000;
            padding: clamp(0.5rem, 2vw, 1rem) 0;
            border-bottom: 1px solid rgba(37, 99, 235, 0.1);
        }
        
        .navbar-content {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 clamp(1rem, 4vw, 2rem);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: nowrap; /* Ensure single line */
            gap: 1rem;
        }
        
        .navbar-logo {
            font-size: clamp(1.2rem, 3vw, 1.8rem);
            font-weight: 800;
            color: #2563eb;
            text-decoration: none;
            background: linear-gradient(135deg, #2563eb, #1e40af);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 2px 4px rgba(37, 99, 235, 0.1);
            margin-right: 2rem;
            flex-shrink: 0;
        }
        
        .nav-buttons-container {
            display: flex;
            flex-direction: row;
            gap: clamp(0.5rem, 1vw, 1rem);
            align-items: center;
            flex-wrap: nowrap;
        }
        
        /* Enhanced Button Styles */
        .stButton > button {
            background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 0.75rem !important;
            padding: clamp(0.5rem, 1.5vw, 0.75rem) clamp(1rem, 2vw, 1.5rem) !important;
            font-size: clamp(0.8rem, 1.5vw, 0.95rem) !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            position: relative !important;
            overflow: hidden !important;
            min-height: 44px !important;
            min-width: fit-content !important;
            white-space: nowrap !important;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #1e40af, #2563eb) !important;
            transform: translateY(-2px) scale(1.02) !important;
            box-shadow: 0 8px 25px rgba(37, 99, 235, 0.4) !important;
            color: #ffffff !important;
        }
        
        .stButton > button:active {
            transform: translateY(0) scale(0.98) !important;
            box-shadow: 0 2px 10px rgba(37, 99, 235, 0.3) !important;
        }
        
        .stButton > button:focus {
            outline: 2px solid rgba(37, 99, 235, 0.5) !important;
            outline-offset: 2px !important;
        }
        
        /* Ripple Effect */
        .stButton > button::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        
        .stButton > button:active::before {
            width: 300px;
            height: 300px;
        }
        
        /* Current Page Highlighting */
        .stButton[data-current="true"] > button {
            background: linear-gradient(135deg, #1e40af, #1d4ed8) !important;
            box-shadow: 0 6px 20px rgba(30, 64, 175, 0.4) !important;
            transform: translateY(-1px) !important;
        }
        
        /* Mobile Responsiveness */
        @media (max-width: 768px) {
            .navbar-content {
                flex-direction: column;
                gap: 0.75rem;
                padding: 0.75rem 1rem;
                align-items: stretch;
            }
            
            .nav-buttons-container {
                width: 100%;
                justify-content: center;
                flex-wrap: wrap;
                gap: 0.5rem;
            }
            
            .stButton > button {
                padding: 0.6rem 1rem !important;
                font-size: 0.85rem !important;
                min-width: calc(50% - 0.25rem) !important;
                flex: 1 1 auto !important;
            }
            
            .navbar-logo {
                font-size: 1.3rem;
            }
        }
        
        @media (max-width: 480px) {
            .stButton > button {
                min-width: 100% !important;
                margin-bottom: 0.25rem !important;
            }
        }
        
        /* Loading Animation */
        .navbar-container.loading {
            animation: slideDown 0.5s ease-out;
        }
        
        @keyframes slideDown {
            from {
                transform: translateY(-100%);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        /* Accessibility Improvements */
        .stButton > button:focus-visible {
            outline: 3px solid rgba(37, 99, 235, 0.6) !important;
            outline-offset: 2px !important;
        }
        
        /* Dark Mode Support */
        @media (prefers-color-scheme: dark) {
            .navbar-container {
                background: rgba(15, 23, 42, 0.95);
                border-bottom: 1px solid rgba(37, 99, 235, 0.2);
            }
        }
        
        /* High Contrast Mode */
        @media (prefers-contrast: high) {
            .stButton > button {
                border: 2px solid #ffffff !important;
            }
        }
        
        /* Reduced Motion */
        @media (prefers-reduced-motion: reduce) {
            .stButton > button,
            .navbar-container {
                transition: none !important;
                animation: none !important;
            }
        }
        
        /* Spacer for fixed navbar */
        .navbar-spacer {
            height: clamp(70px, 10vw, 90px);
            width: 100%;
        }
        </style>
        
        <script>
        // Enhanced JavaScript for navbar functionality
        document.addEventListener('DOMContentLoaded', function() {
            // Add loading animation to navbar
            const navbar = document.querySelector('.navbar-container');
            if (navbar) {
                navbar.classList.add('loading');
            }
            
            // Smooth scroll behavior for better UX
            document.documentElement.style.scrollBehavior = 'smooth';
            
            // Add intersection observer for navbar transparency
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    const navbar = document.querySelector('.navbar-container');
                    if (navbar) {
                        if (entry.isIntersecting) {
                            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
                        } else {
                            navbar.style.background = 'rgba(255, 255, 255, 0.98)';
                        }
                    }
                });
            }, { threshold: 0.1 });
            
            // Observe the first section if it exists
            const firstSection = document.querySelector('.hero-section, .main-content');
            if (firstSection) {
                observer.observe(firstSection);
            }
            
            // Add keyboard navigation support
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Tab') {
                    document.body.classList.add('keyboard-navigation');
                }
            });
            
            document.addEventListener('mousedown', function() {
                document.body.classList.remove('keyboard-navigation');
            });
        });
        </script>
    """, unsafe_allow_html=True)
    
    # Create navbar structure
    st.markdown('<div class="navbar-container">', unsafe_allow_html=True)
    st.markdown('<div class="navbar-content">', unsafe_allow_html=True)
    st.markdown("""
        <div class="navbar-logo">
            HealthAssist
        </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="nav-buttons-container">', unsafe_allow_html=True)

    # Determine columns based on which buttons are shown
    cols = []
    if show_home:
        cols.append('home')
    if show_symptom_btn:
        cols.append('symptom')
    if show_checkup_btn:
        cols.append('checkup')
    if show_logout:
        cols.append('logout')
    col_objs = st.columns(len(cols)) if cols else []
    col_map = dict(zip(cols, col_objs))

    # Home button
    if 'home' in col_map:
        with col_map['home']:
            home_current = "true" if current_page == 'home' else "false"
            st.markdown(f'<div data-current="{home_current}">', unsafe_allow_html=True)
            st.button('🏠 Home', 
                     key=f'nav_home_{key_suffix}', 
                     on_click=lambda: on_navigate('home'),
                     use_container_width=True,
                     help="Go to home page")
            st.markdown('</div>', unsafe_allow_html=True)

    # Symptom Checker button (always redirects to wizard)
    if 'symptom' in col_map:
        with col_map['symptom']:
            wizard_current = "true" if current_page == 'wizard' else "false"
            st.markdown(f'<div data-current="{wizard_current}">', unsafe_allow_html=True)
            st.button('🔍 Symptom Checker',
                     key=f'nav_wizard_{key_suffix}',
                     on_click=lambda: on_navigate('wizard'),
                     use_container_width=True,
                     help="Check your symptoms")
            st.markdown('</div>', unsafe_allow_html=True)

    # Start Checkup button (always redirects to chat)
    if 'checkup' in col_map:
        with col_map['checkup']:
            chat_current = "true" if current_page == 'chat' else "false"
            st.markdown(f'<div data-current="{chat_current}">', unsafe_allow_html=True)
            st.button('💬 Start Checkup',
                     key=f'nav_checkup_{key_suffix}',
                     on_click=lambda: on_navigate('chat'),
                     use_container_width=True,
                     help="Start a medical consultation")
            st.markdown('</div>', unsafe_allow_html=True)

    # Logout button (only on chat page)
    if 'logout' in col_map and on_logout:
        with col_map['logout']:
            st.button('🚪 Logout',
                     key=f'nav_logout_{key_suffix}',
                     on_click=on_logout,
                     use_container_width=True,
                     help="Sign out of your account")

    st.markdown('</div>', unsafe_allow_html=True)  # Close nav-buttons-container
    st.markdown('</div>', unsafe_allow_html=True)  # Close navbar-content
    st.markdown('</div>', unsafe_allow_html=True)  # Close navbar-container
    
    # Add spacer to prevent content from hiding behind fixed navbar
    st.markdown('<div class="navbar-spacer"></div>', unsafe_allow_html=True)
import streamlit as st
import components.navigation as navigation

def render(on_start_checkup):
    # Initialize session state for checkup trigger
    if "checkup_triggered" not in st.session_state:
        st.session_state.checkup_triggered = False

    # Apply custom CSS (remove navbar styles and references)
    st.markdown("""
        <style>
        /* Global Reset and Base Styles */
        html, body, .main, .block-container, .stApp {
            margin: 0 !important;
            padding: 0 !important;
            width: 100vw !important;
            overflow-x: hidden !important;
            font-family: 'Inter', sans-serif;
            font-size: clamp(14px, 2vw, 16px);
        }

        /* Hide Streamlit UI Elements (Navbar, Sidebar, Toolbar, etc.) */
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stMainMenu"],
        [data-testid="stSidebar"],
        [data-testid="collapsedControl"],
        section[data-testid="stSidebarNav"],
        .css-1lcbmhc.e1fqkh3o3,
        .stSidebar,
        .stSidebarNav,
        header,
        .stApp > header {
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            height: 0 !important;
        }

        /* Ensure Main Content Fills Space */
        .main .block-container {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }

        /* Remove Gaps Between Sections */
        .hero-section, .features-section, .stats-section, .testimonials-section, .contact-section {
            margin: 0 !important;
            padding: 2.5rem 0 !important;
        }
        footer {
            margin: 0 !important;
            padding: clamp(1rem, 2vw, 1.5rem) !important;
        }

        /* Animation Keyframes */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-10px); }
            60% { transform: translateY(-5px); }
        }
        @keyframes ripple {
            to { transform: scale(4); opacity: 0; }
        }
        @keyframes underline {
            from { width: 0; }
            to { width: 100%; }
        }
        @keyframes glow {
            0% { text-shadow: 0 0 5px rgba(37, 99, 235, 0.5); }
            50% { text-shadow: 0 0 10px rgba(37, 99, 235, 0.8); }
            100% { text-shadow: 0 0 5px rgba(37, 99, 235, 0.5); }
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        @keyframes scrollPulse {
            0% { transform: translateY(0); opacity: 0.8; }
            50% { transform: translateY(10px); opacity: 1; }
            100% { transform: translateY(0); opacity: 0.8; }
        }
        @keyframes slideIn {
            from { transform: translateX(100%); }
            to { transform: translateX(0); }
        }

        /* Respect Reduced Motion */
        @media (prefers-reduced-motion: reduce) {
            .hero-content, .feature-card, .stats-card, .testimonial, .section,
            .cta-button, .form-button, .ripple, .feature-card img, .nav-menu {
                animation: none !important;
                transition: none !important;
            }
        }

        /* Container for Centered Content */
        .container {
            max-width: min(90vw, 1920px);
            margin: 0 auto;
            padding: 0 clamp(8px, 2vw, 16px);
        }

        /* Hero Section */
        .hero-section {
            background: linear-gradient(to right, #3b82f6, #1e40af);
            padding: clamp(6rem, 10vw, 8rem) clamp(0.5rem, 2vw, 1rem) clamp(2rem, 5vw, 4rem);
            text-align: center;
            position: relative;
            overflow: hidden;
            margin-top: clamp(3rem, 5vw, 4rem);
        }
        .hero-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('https://source.unsplash.com/random/1200x600/?healthcare') no-repeat center center/cover;
            opacity: 0.2;
            z-index: 0;
        }
        .hero-content {
            z-index: 1;
            animation: fadeInUp 1s ease-in;
        }
        .hero-section h1 {
            font-size: clamp(1.5rem, 5vw, 3.5rem);
            font-weight: 800;
            color: #fff;
            margin-bottom: clamp(0.5rem, 2vw, 1rem);
        }
        .hero-section p {
            color: #dbeafe;
            font-size: clamp(0.9rem, 2.5vw, 1.2rem);
            max-width: 600px;
            margin: 0 auto clamp(1rem, 2vw, 2rem);
            animation: fadeInUp 1.2s ease-in;
        }
        .hero-buttons {
            display: flex;
            gap: clamp(0.5rem, 2vw, 1rem);
            justify-content: center;
            flex-wrap: wrap;
        }
        .scroll-indicator {
            position: absolute;
            bottom: 1rem;
            left: 50%;
            transform: translateX(-50%);
            color: #fff;
            font-size: clamp(1rem, 3vw, 2rem);
            animation: scrollPulse 2s infinite;
            cursor: pointer;
        }
        .cta-button {
            position: relative;
            overflow: hidden;
            background: #2563eb;
            color: #fff !important;
            padding: clamp(0.75rem, 2vw, 1rem) clamp(1.5rem, 3vw, 2rem);
            border-radius: 0.75rem;
            font-size: clamp(0.9rem, 2vw, 1.1rem);
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            transition: transform 0.2s, background 0.2s, box-shadow 0.2s;
            text-align: center;
            cursor: pointer;
            text-decoration: none;
            min-height: 48px;
            display: inline-block;
        }
        .cta-button:hover {
            background: #1e40af;
            color: #fff !important;
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        .cta-button:active {
            transform: scale(0.95);
        }
        .cta-button .ripple {
            position: absolute;
            background: rgba(255,255,255,0.3);
            border-radius: 50%;
            width: clamp(10px, 2vw, 20px);
            height: clamp(10px, 2vw, 20px);
            animation: ripple 0.6s linear;
            pointer-events: none;
        }

        /* Features Section */
        .features-section {
            padding: clamp(2rem, 5vw, 4rem) clamp(0.5rem, 2vw, 1rem);
            text-align: center;
            background: #f9fafb;
        }
        .features-section h2 {
            color: #2563eb;
            text-transform: uppercase;
            font-weight: 600;
            font-size: clamp(0.8rem, 2vw, 1.2rem);
            letter-spacing: 1px;
        }
        .features-section h3 {
            font-size: clamp(1.2rem, 4vw, 2rem);
            font-weight: 800;
            margin-top: 0.5rem;
        }
        .features-section p {
            max-width: 700px;
            margin: 1rem auto;
            color: #6b7280;
            font-size: clamp(0.8rem, 2vw, 1rem);
        }
        .features-grid {
            margin-top: clamp(2rem, 5vw, 4rem);
            display: grid;
            grid-template-columns: 1fr;
            gap: clamp(1rem, 3vw, 2rem);
            justify-items: center;
        }
        .feature-card {
            background: #fff;
            padding: clamp(1rem, 3vw, 2rem);
            border-radius: 1rem;
            width: 100%;
            max-width: 300px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
            opacity: 0;
        }
        .feature-card.visible {
            animation: fadeInUp 0.5s ease-in forwards;
        }
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }
        .feature-card img {
            width: clamp(32px, 5vw, 48px);
            height: clamp(32px, 5vw, 48px);
            margin-bottom: 1rem;
            transition: transform 0.2s;
        }
        .feature-card:hover img {
            animation: bounce 0.4s;
        }
        .feature-card h4 {
            font-size: clamp(0.9rem, 2.5vw, 1.25rem);
            margin: 0.5rem 0;
        }

        /* Stats Section */
        .stats-section {
            background: linear-gradient(to right, #1e40af, #3b82f6);
            color: #fff;
            padding: clamp(2rem, 5vw, 4rem) clamp(0.5rem, 2vw, 1rem);
            text-align: center;
        }
        .stats-section h2 {
            font-size: clamp(1.2rem, 4vw, 2rem);
            font-weight: 800;
        }
        .stats-section p {
            margin-top: 1rem;
            font-size: clamp(0.8rem, 2vw, 1.1rem);
            color: #dbeafe;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: clamp(1rem, 3vw, 2rem);
            margin-top: clamp(1rem, 3vw, 2rem);
            justify-items: center;
        }
        .stats-card {
            text-align: center;
            padding: clamp(0.5rem, 2vw, 1rem);
            opacity: 0;
            transition: transform 0.2s;
        }
        .stats-card.visible {
            animation: fadeInUp 0.5s ease-in forwards;
            animation-delay: 0.2s;
        }
        .stats-card:hover {
            transform: scale(1.05);
        }
        .stats-card.animate-pulse {
            animation: pulse 0.5s ease-in-out;
        }
        .stats-card h3 {
            font-size: clamp(1rem, 3vw, 1.8rem);
            font-weight: bold;
        }

        /* Testimonials Section */
        .testimonials-section {
            padding: clamp(2rem, 5vw, 4rem) clamp(0.5rem, 2vw, 1rem);
            background: #f0f4ff;
            text-align: center;
        }
        .testimonials-section h2 {
            color: #2563eb;
            text-transform: uppercase;
            font-weight: 600;
            font-size: clamp(0.8rem, 2vw, 1.2rem);
            letter-spacing: 1px;
        }
        .testimonials-section h3 {
            font-size: clamp(1.2rem, 4vw, 2rem);
            font-weight: 800;
            margin-top: 0.5rem;
        }
        .testimonials-grid {
            margin-top: clamp(1rem, 3vw, 2rem);
            display: grid;
            grid-template-columns: 1fr;
            gap: clamp(1rem, 3vw, 2rem);
            justify-items: center;
        }
        .testimonial {
            background: #fff;
            padding: clamp(1rem, 3vw, 2rem);
            border-radius: 1rem;
            width: 100%;
            max-width: 320px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: transform 0.3s;
            opacity: 0;
        }
        .testimonial.visible {
            animation: fadeInUp 0.5s ease-in forwards;
        }
        .testimonial:nth-child(1).visible { animation-delay: 0.1s; }
        .testimonial:nth-child(2).visible { animation-delay: 0.2s; }
        .testimonial:nth-child(3).visible { animation-delay: 0.3s; }
        .testimonial:hover {
            transform: scale(1.03);
        }
        .testimonial p:first-child {
            color: #374151;
            font-size: clamp(0.8rem, 2vw, 1rem);
            transition: text-shadow 0.3s;
        }
        .testimonial:hover p:first-child {
            animation: glow 1s infinite;
        }
        .testimonial img {
            width: clamp(32px, 5vw, 40px);
            height: clamp(32px, 5vw, 40px);
            border-radius: 50%;
            margin-bottom: 1rem;
        }

        /* Contact Section */
        .contact-section {
            padding: clamp(2rem, 5vw, 4rem) clamp(0.5rem, 2vw, 1rem);
            background: linear-gradient(to right, #1e40af, #3b82f6);
            color: #fff;
            text-align: center;
        }
        .contact-section h2 {
            font-size: clamp(1.2rem, 4vw, 2rem);
            font-weight: 800;
        }
        .contact-section p {
            margin-top: 1rem;
            font-size: clamp(0.8rem, 2vw, 1rem);
            color: #dbeafe;
        }
        .contact-form input, .contact-form textarea {
            width: 100%;
            padding: clamp(0.5rem, 2vw, 0.75rem);
            border: none;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            font-size: clamp(0.8rem, 2vw, 1rem);
            position: relative;
            transition: transform 0.2s;
            background: #fff;
        }
        .contact-form input::after, .contact-form textarea::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 0;
            height: 2px;
            background: #2563eb;
            transition: width 0.3s;
        }
        .contact-form input:focus::after, .contact-form textarea:focus::after {
            width: 100%;
            animation: underline 0.3s forwards;
        }
        .contact-form input:focus, .contact-form textarea:focus {
            transform: scale(1.02);
            outline: none;
        }
        .form-button {
            position: relative;
            overflow: hidden;
            background: #2563eb;
            color: #fff;
            padding: clamp(0.75rem, 2vw, 1rem) clamp(1.5rem, 3vw, 2rem);
            border-radius: 0.75rem;
            font-size: clamp(0.9rem, 2vw, 1.1rem);
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            transition: background 0.2s, transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
            width: 100%;
            text-align: center;
            min-height: 48px;
        }
        .form-button:hover {
            background: #1e40af;
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            animation: bounce 0.4s;
        }
        .form-button:active {
            transform: scale(0.95);
        }
        .form-button .ripple {
            position: absolute;
            background: rgba(255,255,255,0.3);
            border-radius: 50%;
            width: clamp(10px, 2vw, 20px);
            height: clamp(10px, 2vw, 20px);
            animation: ripple 0.6s linear;
            pointer-events: none;
        }
        .spinner {
            display: none;
            width: clamp(16px, 2vw, 20px);
            height: clamp(16px, 2vw, 20px);
            border: 2px solid #fff;
            border-top: 2px solid transparent;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin: 0 auto;
        }
        .spinner.active {
            display: block;
        }

        /* Footer Styles */
        footer {
            background: #1e40af;
            color: #fff;
            text-align: center;
            padding: clamp(1rem, 2vw, 1.5rem);
            font-size: clamp(0.8rem, 2vw, 1rem);
            opacity: 0.9;
        }
        footer p {
            margin: 0;
        }

        /* Responsive Breakpoints */
        @media (max-width: 767px) {
            .nav-menu {
                display: none;
                position: fixed;
                top: clamp(3rem, 5vw, 4rem);
                right: 0;
                width: 70%;
                height: 100vh;
                background: rgba(255, 255, 255, 0.95);
                flex-direction: column;
                padding: 1rem;
                box-shadow: -2px 0 4px rgba(0,0,0,0.1);
                animation: slideIn 0.3s ease-in;
            }
            .nav-menu.active {
                display: flex;
            }
            .nav-item {
                margin: 0.5rem 0;
            }
            .hamburger {
                display: block;
            }
            .hero-buttons {
                flex-direction: column;
                align-items: center;
            }
            .cta-button {
                width: 100%;
                max-width: 300px;
            }
        }
        @media (min-width: 576px) {
            .features-grid, .stats-grid, .testimonials-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        @media (min-width: 768px) {
            .features-grid, .testimonials-grid {
                grid-template-columns: repeat(3, 1fr);
            }
            .stats-grid {
                grid-template-columns: repeat(3, 1fr);
            }
            .hero-section h1 {
                font-size: clamp(2rem, 5vw, 3rem);
            }
            .cta-button, .form-button {
                width: auto;
                min-width: 200px;
            }
        }
        @media (min-width: 1024px) {
            .container {
                max-width: min(85vw, 1440px);
            }
            .hero-section::before {
                background-image: url('https://source.unsplash.com/random/1920x1080/?healthcare');
            }
            .feature-card, .testimonial {
                max-width: 360px;
            }
            .cta-button, .form-button {
                padding: clamp(0.75rem, 1.5vw, 1rem) clamp(1.5rem, 2vw, 2rem);
            }
            .scroll-indicator {
                font-size: 2rem;
            }
        }
        @media (min-width: 1440px) {
            .container {
                max-width: min(80vw, 1920px);
            }
            .hero-section h1 {
                font-size: clamp(2.5rem, 4vw, 3.5rem);
            }
            .feature-card, .testimonial {
                max-width: 400px;
            }
            .cta-button, .form-button {
                font-size: clamp(1rem, 1.5vw, 1.2rem);
            }
            .feature-card, .stats-card, .testimonial {
                box-shadow: 0 4px 16px rgba(0,0,0,0.15);
            }
        }
        @media (min-width: 1920px) {
            .hero-section::before {
                background-image: url('https://source.unsplash.com/random/3840x2160/?healthcare');
            }
            .hero-section h1 {
                font-size: clamp(3rem, 3.5vw, 4rem);
            }
            .cta-button .ripple, .form-button .ripple {
                width: 30px;
                height: 30px;
            }
            footer {
                font-size: clamp(0.9rem, 1.5vw, 1.2rem);
                padding: clamp(1.5rem, 2vw, 2rem);
            }
        }

        /* Accessibility */
        .cta-button:focus, .form-button:focus, .nav-link:focus {
            outline: 3px solid #2563eb;
            outline-offset: 2px;
        }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    # Use the shared navigation component
    navigation.render(
        on_navigate=lambda page: st.session_state.update(current_page=page),
        current_page='home',
        on_logout=lambda: st.session_state.update(auth_token=None, user_info=None, current_page='login'),
        show_checkup=True,
        show_symptom=True,
        key_suffix='home_page'
    )

    # Hero Section with Buttons
    st.markdown("""
        <div class="hero-section">
            <div class="container">
                <div class="hero-content">
                    <h1>Healthcare powered by <span style='color: #bfdbfe;'>AI</span></h1>
                    <p>Check your symptoms, get instant health insights, and receive guidance on next steps, all powered by advanced medical AI.</p>
                    <div class="hero-buttons">
                        <a href="#" class="cta-button" id="start-checkup-hero" aria-label="Start Symptom Check" role="button">Start Checkup →</a>
                        <a href="https://github.com/JOHNMARK2334/final-year-project/blob/main/Readme.md" class="cta-button" target="_blank" aria-label="Learn More" role="button">Learn More ↗</a>
                    </div>
                </div>
            </div>
            <div class="scroll-indicator" aria-hidden="true">↓</div>
        </div>
    """, unsafe_allow_html=True)

    # Features Section
    st.markdown("""
        <div class="features-section section">
            <div class="container">
                <h2>Features</h2>
                <h3>Healthcare support at your fingertips</h3>
                <p>Our platform uses the latest advancements in medical AI to provide accurate and personalized health information.</p>
                <div class="features-grid">
                    <div class="feature-card visible">
                        <img src="https://img.icons8.com/color/48/000000/chat.png" alt="Conversational Interface Icon" loading="lazy">
                        <h4>Conversational Interface</h4>
                        <p>Natural dialogue with our AI to describe your symptoms in your own words.</p>
                    </div>
                    <div class="feature-card visible">
                        <img src="https://img.icons8.com/color/48/000000/search.png" alt="Symptom Analysis Icon" loading="lazy">
                        <h4>Symptom Analysis</h4>
                        <p>Advanced algorithms analyze your symptoms to provide potential causes.</p>
                    </div>
                    <div class="feature-card visible">
                        <img src="https://img.icons8.com/color/48/000000/medical-doctor.png" alt="Medical Expertise Icon" loading="lazy">
                        <h4>Medical Expertise</h4>
                        <p>Built on knowledge from medical professionals and clinical guidelines.</p>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Stats Section
    st.markdown("""
        <div class="stats-section section">
            <div class="container">
                <h2>Trusted by patients worldwide</h2>
                <p>Our platform has helped millions of people understand their health concerns</p>
                <div class="stats-grid">
                    <div class="stats-card visible">
                        <h3>5M+</h3>
                        <p>Health assessments</p>
                    </div>
                    <div class="stats-card visible">
                        <h3>150+</h3>
                        <p>Countries served</p>
                    </div>
                    <div class="stats-card visible">
                        <h3>98%</h3>
                        <p>Satisfaction rate</p>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Testimonials Section
    st.markdown("""
        <div class="testimonials-section section">
            <div class="container">
                <h2>Testimonials</h2>
                <h3>What our users are saying</h3>
                <div class="testimonials-grid">
                    <div class="testimonial visible">
                        <img src="https://randomuser.me/api/portraits/women/1.jpg" alt="Sarah M. Avatar" loading="lazy">
                        <p>"I described my symptoms and within seconds got a detailed, helpful explanation. Amazing!"</p>
                        <p style="margin-top: 1rem; font-weight: 600; color: #1e3a8a;">— Sarah M.</p>
                    </div>
                    <div class="testimonial visible">
                        <img src="https://randomuser.me/api/portraits/men/2.jpg" alt="Daniel K. Avatar" loading="lazy">
                        <p>"I used this tool late at night when clinics were closed. It really calmed my anxiety."</p>
                        <p style="margin-top: 1rem; font-weight: 600; color: #1e3a8a;">— Daniel K.</p>
                    </div>
                    <div class="testimonial visible">
                        <img src="https://randomuser.me/api/portraits/women/3.jpg" alt="Priya R. Avatar" loading="lazy">
                        <p>"Highly recommend to anyone looking for trustworthy symptom guidance. 10/10."</p>
                        <p style="margin-top: 1rem; font-weight: 600; color: #1e3a8a;">— Priya R.</p>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Contact Section
    st.markdown("""
        <div class="contact-section section">
            <div class="container">
                <h2>Have Questions? Get in Touch!</h2>
                <p>We're here to help with any feedback, support, or partnership inquiries.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Contact Form
    if st.session_state.get("clear_contact_form"):
        st.session_state["contact_name"] = ""
        st.session_state["contact_email"] = ""
        st.session_state["contact_message"] = ""
        st.session_state["clear_contact_form"] = False

    with st.form("contact_form", clear_on_submit=True):
        st.markdown('<div class="contact-form container">', unsafe_allow_html=True)
        name = st.text_input("Your Name", key="contact_name", placeholder="Enter your name")
        email = st.text_input("Your Email", key="contact_email", placeholder="Enter your email")
        message = st.text_area("Your Message", key="contact_message", placeholder="Enter your message")
        st.markdown('<button type="submit" class="form-button" aria-label="Send Message" role="button">Send Message</button>', unsafe_allow_html=True)
        st.markdown('<div class="spinner" id="form-spinner"></div>', unsafe_allow_html=True)
        submitted = st.form_submit_button("", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if submitted:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            try:
                smtp_server = "smtp.gmail.com"
                smtp_port = 587
                smtp_user = "jj90773162@gmail.com"
                smtp_password = "bebt reqw nvxe lgjp"
                msg = MIMEMultipart()
                msg["From"] = smtp_user
                msg["To"] = "jj90773162@gmail.com"
                msg["Subject"] = f"Contact Form Submission from {name}"
                body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
                msg.attach(MIMEText(body, "plain"))
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, "jj90773162@gmail.com", msg.as_string())
                server.quit()
                st.success("Your message has been sent!", emoji="✅")
                st.session_state["clear_contact_form"] = True
                st.rerun()
            except Exception as e:
                st.error(f"Failed to send message: {e}", emoji="🔥")

    # Footer (Last Element)
    st.markdown("""
        <footer aria-label="Footer">
            <p>Copyright © 2025 HealthAssist</p>
        </footer>
    </div>
    """, unsafe_allow_html=True)

    # JavaScript for Animations, Micro-Interactions, and Checkup Trigger
    st.markdown("""
        <script>
        // Number Counter Animation
        function animateNumber(element, start, end, suffix = '') {
            let startTimestamp = null;
            const step = (timestamp) => {
                if (!startTimestamp) startTimestamp = timestamp;
                const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                const value = Math.floor(progress * (end - start) + start);
                element.textContent = value + suffix;
                if (progress < 1) {
                    window.requestAnimationFrame(step);
                }
            };
            window.requestAnimationFrame(step);
        }

        // JavaScript for Interactions
        document.addEventListener('DOMContentLoaded', () => {
            // Hamburger Menu Toggle
            const hamburger = document.querySelector('.hamburger');
            const navMenu = document.querySelector('.nav-menu');
            hamburger.addEventListener('click', () => {
                navMenu.classList.toggle('active');
                const expanded = hamburger.getAttribute('aria-expanded') === 'true';
                hamburger.setAttribute('aria-expanded', !expanded);
                hamburger.textContent = expanded ? '☰' : '✕';
            });

            // Ripple Effect for Buttons
            const buttons = document.querySelectorAll('.cta-button, .form-button, .nav-link');
            buttons.forEach(button => {
                button.addEventListener('click', (e) => {
                    const ripple = document.createElement('span');
                    ripple.classList.add('ripple');
                    const rect = button.getBoundingClientRect();
                    const size = Math.max(rect.width, rect.height);
                    ripple.style.width = ripple.style.height = size + 'px';
                    ripple.style.left = e.clientX - rect.left - size / 2 + 'px';
                    ripple.style.top = e.clientY - rect.top - size / 2 + 'px';
                    button.appendChild(ripple);
                    setTimeout(() => ripple.remove(), 600);
                });
            });

            // Start Checkup Button Handlers
            const startCheckupNav = document.querySelector('#start-checkup-nav');
            const startCheckupHero = document.querySelector('#start-checkup-hero');
            if (startCheckupNav) {
                startCheckupNav.addEventListener('click', (e) => {
                    e.preventDefault();
                    // Set session state flag
                    fetch('/start-checkup', { method: 'POST' })
                        .then(() => {
                            window.__streamlit_checkup_triggered = true;
                        });
                });
            }
            if (startCheckupHero) {
                startCheckupHero.addEventListener('click', (e) => {
                    e.preventDefault();
                    // Set session state flag
                    fetch('/start-checkup', { method: 'POST' })
                        .then(() => {
                            window.__streamlit_checkup_triggered = true;
                        });
                });
            }

            // Stats Number Animation
            const stats = [
                selector: '.stats-card:nth-child(1) h3', end: 5000000, suffix: '+' 
                },
                { selector: '.stats-card:nth-child(2) h3', end: 200, suffix: '+' },
                { selector: '.stats-card:nth-child(3) h3', end: 98, suffix: '%' }
            ];
            const statsObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        stats.forEach(stat => {
                            const element = document.querySelector(stat.selector);
                            element.parentElement.classList.add('animate-pulse', 'visible');
                            animateNumber(element, 0, stat.end, 2000, stat.suffix);
                        });
                        statsObserver.disconnect();
                    }
                });
            }, { threshold: 0.5 });
            statsObserver.observe(document.querySelector('.stats-section'));

            // Section and Card Animations
            const sections = document.querySelectorAll('.section');
            const cards = document.querySelectorAll('.feature-card, .testimonial');
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                        if (entry.target.classList.contains('section')) {
                            entry.target.querySelectorAll('.feature-card, .testimonial').forEach(card => {
                                card.classList.add('visible');
                            });
                        }
                    }
                });
            }, { threshold: 0.1 });
            sections.forEach(section => observer.observe(section));
            cards.forEach(card => observer.observe(card));

            // Scroll Indicator Hiding
            const scrollIndicator = document.querySelector('.scroll-indicator');
            window.addEventListener('scroll', () => {
                if (window.scrollY > 100) {
                    scrollIndicator.style.opacity = '0';
                    scrollIndicator.style.pointerEvents = 'none';
                } else {
                    scrollIndicator.style.opacity = '1';
                    scrollIndicator.style.pointerEvents = 'auto';
                }
            });

            // Form Submission Spinner
            const form = document.querySelector('form');
            const spinner = document.querySelector('#form-spinner');
            form.addEventListener('submit', () => {
                spinner.classList.add('active');
                setTimeout(() => spinner.classList.remove('active'), 2000);
            });
        });

        // Streamlit Checkup Trigger
        function checkStreamlitTrigger() {
            if (window.__streamlit_checkup_triggered) {
                window.__streamlit_checkup_triggered = false;
                // Signal Python to check session state
                window.location.reload();
            }
        }
        setInterval(checkStreamlitTrigger, 200);
        </script>
    """, unsafe_allow_html=True)

    # Check for Checkup Trigger
    if st.session_state.checkup_triggered:
        st.session_state.checkup_triggered = False
        on_start_checkup()
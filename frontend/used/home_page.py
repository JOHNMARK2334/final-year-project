import streamlit as st

def render(on_start_checkup):
    query_params = st.query_params # Replaced st.experimental_get_query_params
    if query_params.get("page_action") == "start_checkup_home": # Adjusted to check for string, not list
        st.query_params.clear()  # Replaced st.experimental_set_query_params()
        on_start_checkup()
        # app.py's set_page (called by on_start_checkup) will handle st.rerun()

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
        .hero-section, .features-section, .stats-section, .testimonials-section, 
        .contact-section, footer {
            margin: 0 !important; /* Keep this to prevent external margins */
        }

        /* Animation Keyframes */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); } /* Kept for reference, but animations using it will be removed */
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
            /* animation: fadeInUp 1s ease-in; */ /* Animation removed */
            opacity: 1; /* Ensure visible */
        }
        .hero-section h1 {
            font-size: clamp(1.5rem, 5vw, 3.5rem);
            font-weight: 800;
            color: #fff;
            margin-bottom: clamp(0.5rem, 2vw, 1rem);
        }
        .hero-section p {
            color: #f0f0f0; /* Text color changed to light gray for better contrast */
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
            padding: clamp(3rem, 6vw, 5rem) clamp(1rem, 3vw, 2rem); /* Updated padding */
            text-align: center;
            background: #f9fafb; /* Light background, black text will be fine */
        }
        .features-section h2 {
            color: black; /* Text color changed */
            text-transform: uppercase;
            font-weight: 600;
            font-size: clamp(0.8rem, 2vw, 1.2rem);
            letter-spacing: 1px;
        }
        .features-section h3 {
            font-size: clamp(1.2rem, 4vw, 2rem);
            font-weight: 800;
            margin-top: 0.5rem;
            color: black; /* Text color changed */
        }
        .features-section p {
            max-width: 700px;
            margin: 1rem auto;
            color: black; /* Text color changed */
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
            opacity: 1; /* Changed from 0 to 1 */
        }
        .feature-card.visible {
            /* animation: fadeInUp 0.5s ease-in forwards; */ /* Animation removed */
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
            color: black; /* Text color changed */
        }
        /* Assuming feature-card might have a p tag directly */
        .feature-card p {
            color: black; /* Text color changed */
        }

        /* Stats Section */
        .stats-section {
            background: linear-gradient(to right, #1e40af, #3b82f6); /* Dark background */
            color: #f0f0f0; /* Default text color for section changed to light gray */
            padding: clamp(3rem, 6vw, 5rem) clamp(1rem, 3vw, 2rem); /* Updated padding */
            text-align: center;
        }
        .stats-section h2 {
            font-size: clamp(1.2rem, 4vw, 2rem);
            font-weight: 800;
            color: #fff; /* Text color changed to white */
        }
        .stats-section p {
            margin-top: 1rem;
            font-size: clamp(0.8rem, 2vw, 1.1rem);
            color: #f0f0f0; /* Text color changed to light gray */
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
            opacity: 1; /* Changed from 0 to 1 */
            transition: transform 0.2s;
        }
        .stats-card.visible {
            /* animation: fadeInUp 0.5s ease-in forwards; */ /* Animation removed */
            /* animation-delay: 0.2s; */ /* No longer needed */
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
            color: #fff; /* Text color changed to white */
        }
        /* Assuming stats-card has a p tag directly for its description */
        .stats-card p {
            color: #f0f0f0; /* Text color changed to light gray */
        }

        /* Testimonials Section */
        .testimonials-section {
            padding: clamp(3rem, 6vw, 5rem) clamp(1rem, 3vw, 2rem); /* Updated padding */
            background: #f0f4ff; /* Light background, black text will be fine */
            text-align: center;
        }
        .testimonials-section h2 {
            color: black; /* Text color changed */
            text-transform: uppercase;
            font-weight: 600;
            font-size: clamp(0.8rem, 2vw, 1.2rem);
            letter-spacing: 1px;
        }
        .testimonials-section h3 {
            font-size: clamp(1.2rem, 4vw, 2rem);
            font-weight: 800;
            margin-top: 0.5rem;
            color: black; /* Text color changed */
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
            opacity: 1; /* Changed from 0 to 1 */
        }
        .testimonial.visible {
            /* animation: fadeInUp 0.5s ease-in forwards; */ /* Animation removed */
        }
        /* .testimonial:nth-child(1).visible { animation-delay: 0.1s; } */ /* No longer needed */
        /* .testimonial:nth-child(2).visible { animation-delay: 0.2s; } */ /* No longer needed */
        /* .testimonial:nth-child(3).visible { animation-delay: 0.3s; } */ /* No longer needed */
        .testimonial:hover {
            transform: scale(1.03);
        }
        .testimonial img { /* Added this new rule */
            border-radius: 50%; /* Makes the image round */
            width: 80px; /* Example size, adjust as needed */
            height: 80px; /* Example size, adjust as needed */
            object-fit: cover; /* Ensures the image covers the area without distortion */
            margin-bottom: 1rem;
        }
        .testimonial p { /* Targeting all p tags within testimonial */
            color: black; /* Text color changed */
            font-size: clamp(0.8rem, 2vw, 1rem);
            transition: text-shadow 0.3s;
        }
        .testimonial p[style*="font-weight: 600"] { /* Specifically target author if needed, though above should cover */
            color: black !important; /* Ensure override if specific styles were stronger */
        }

        /* Contact Section */
        .contact-section {
            padding: clamp(3rem, 6vw, 5rem) clamp(1rem, 3vw, 2rem); /* Updated padding */
            background: linear-gradient(to right, #1e40af, #3b82f6); /* Dark background */
            color: #f0f0f0; /* Default text color for section changed to light gray */
            text-align: center;
        }
        .contact-section h2 {
            font-size: clamp(1.2rem, 4vw, 2rem);
            font-weight: 800;
            color: #fff; /* Text color changed to white */
        }
        .contact-section p {
            margin-top: 1rem;
            font-size: clamp(0.8rem, 2vw, 1rem);
            color: #f0f0f0; /* Text color changed to light gray */
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
            background: #1e40af; /* Dark background */
            color: #f0f0f0; /* Text color changed to light gray */
            text-align: center;
            /* padding: clamp(1.5rem, 4vw, 2.5rem) clamp(1rem, 3vw, 2rem); */ /* Updated padding REMOVED */
            padding: 1rem; /* Adjusted to a smaller, fixed padding */
            font-size: clamp(0.8rem, 2vw, 1rem);
            opacity: 0.9;
        }
        footer p {
            margin: 0;
            color: #f0f0f0; /* Text color changed to light gray */
        }

        /* Responsive Breakpoints */
        @media (max-width: 767px) {
            /* .nav-menu and .hamburger styles removed as local navbar is deleted */
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
                /* padding: clamp(1.5rem, 2vw, 2rem); */ /* REMOVED */
                padding: 1rem; /* Adjusted to a smaller, fixed padding */
            }
        }

        /* Accessibility */
        .cta-button:focus, .form-button:focus { /* Removed .nav-link:focus */
            outline: 3px solid #2563eb;
            outline-offset: 2px;
        }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    # Hero Section with Buttons
    st.markdown("""
        <div class="hero-section">
            <div class="container">
                <div class="hero-content">
                    <h1>Healthcare powered by <span style='color: #bfdbfe;'>AI</span></h1>
                    <p>Check your symptoms, get instant health insights, and receive guidance on next steps, all powered by advanced medical AI.</p>
                    <div class="hero-buttons">
                        <a href="?page_action=start_checkup_home" class="cta-button" id="start-checkup-hero" aria-label="Start Symptom Check" role="button">Start Checkup →</a>
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
                    <div class="feature-card">
                        <img src="https://img.icons8.com/color/48/000000/chat.png" alt="Conversational Interface Icon" loading="lazy">
                        <h4>Conversational Interface</h4>
                        <p>Natural dialogue with our AI to describe your symptoms in your own words.</p>
                    </div>
                    <div class="feature-card">
                        <img src="https://img.icons8.com/color/48/000000/search.png" alt="Symptom Analysis Icon" loading="lazy">
                        <h4>Symptom Analysis</h4>
                        <p>Advanced algorithms analyze your symptoms to provide potential causes.</p>
                    </div>
                    <div class="feature-card">
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
                    <div class="stats-card">
                        <h3>5 M+</h3>
                        <p>Health assessments</p>
                    </div>
                    <div class="stats-card">
                        <h3>10 +</h3>
                        <p>Countries served</p>
                    </div>
                    <div class="stats-card">
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
                    <div class="testimonial">
                        <img src="https://randomuser.me/api/portraits/women/62.jpg" alt="Sarah M. Avatar" loading="lazy">
                        <p>"I described my symptoms and within seconds got a detailed, helpful explanation. Amazing!"</p>
                        <p style="margin-top: 1rem; font-weight: 600; color: #1e3a8a;">— Sarah M.</p>
                    </div>
                    <div class="testimonial">
                        <img src="https://randomuser.me/api/portraits/men/80.jpg" alt="Daniel K. Avatar" loading="lazy">
                        <p>"I used this tool late at night when clinics were closed. It really calmed my anxiety."</p>
                        <p style="margin-top: 1rem; font-weight: 600; color: #1e3a8a;">— Daniel K.</p>
                    </div>
                    <div class="testimonial">
                        <img src="https://randomuser.me/api/portraits/men/54.jpg" alt="Priya R. Avatar" loading="lazy">
                        <p>"Highly recommend to anyone looking for trustworthy symptom guidance. 10/10."</p>
                        <p style="margin-top: 1rem; font-weight: 600; color: #1e3a8a;">— Karanja P.</p>
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
    # Note: If there's custom JavaScript for the '#start-checkup-hero' button that calls 
    # event.preventDefault(), it might interfere with the href navigation.
    # The ripple effect on buttons is typically CSS-driven or uses JS that shouldn't interfere.
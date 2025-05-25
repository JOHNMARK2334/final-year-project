# pages/home_page.py
import streamlit as st

def render(on_start_checkup):
    # Content only - no page config
    st.title("Welcome to HealthAssist")

    # ---------- Hero Section ----------
    st.markdown("""
        <div style="background: linear-gradient(to right, #3b82f6, #1e40af); padding: 4rem 1rem;">
            <div style="max-width: 1200px; margin: auto; display: flex; flex-direction: column; align-items: start;">
                <h1 style="font-size: 3rem; font-weight: 800; color: white;">Healthcare powered by <span style='color: #bfdbfe;'>AI</span></h1>
                <p style="margin-top: 1rem; color: #dbeafe; font-size: 1.2rem; max-width: 600px;">
                    Check your symptoms, get instant health insights, and receive guidance on next steps, all powered by advanced medical AI.
                </p>
                <div style="margin-top: 2rem; display: flex; gap: 1rem;">
                    <button onclick="window.location.href='/?page=chat'" style="padding: 0.75rem 1.5rem; background: white; color: #1d4ed8; font-weight: 600; border: none; border-radius: 0.5rem;">Start Symptom Check →</button>
                    <button style="padding: 0.75rem 1.5rem; background: rgba(30, 64, 175, 0.6); color: white; font-weight: 600; border: none; border-radius: 0.5rem;">Learn More ↗</button>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ---------- Features Section ----------
    st.markdown("""
        <div style="padding: 4rem 1rem; text-align: center;">
            <h2 style="color: #2563eb; text-transform: uppercase; font-weight: 600;">Features</h2>
            <h3 style="font-size: 2rem; font-weight: 800; margin-top: 0.5rem;">Healthcare support at your fingertips</h3>
            <p style="max-width: 700px; margin: auto; margin-top: 1rem; color: #6b7280;">
                Our platform uses the latest advancements in medical AI to provide accurate and personalized health information.
            </p>
            <div style="margin-top: 4rem; display: flex; flex-wrap: wrap; gap: 2rem; justify-content: center;">
                <div style="background: #f9fafb; padding: 2rem; border-radius: 1rem; width: 280px; text-align: center;">
                    <h4>💬 Conversational Interface</h4>
                    <p style="color: #6b7280;">Natural dialogue with our AI to describe your symptoms in your own words.</p>
                </div>
                <div style="background: #f9fafb; padding: 2rem; border-radius: 1rem; width: 280px; text-align: center;">
                    <h4>🔍 Symptom Analysis</h4>
                    <p style="color: #6b7280;">Advanced algorithms analyze your symptoms to provide potential causes.</p>
                </div>
                <div style="background: #f9fafb; padding: 2rem; border-radius: 1rem; width: 280px; text-align: center;">
                    <h4>🏅 Medical Expertise</h4>
                    <p style="color: #6b7280;">Built on knowledge from medical professionals and clinical guidelines.</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ---------- Stats Section ----------
    st.markdown("""
        <div style="background: #1e40af; color: white; padding: 4rem 1rem;">
            <div style="max-width: 1000px; margin: auto; text-align: center;">
                <h2 style="font-size: 2rem; font-weight: 800;">Trusted by patients worldwide</h2>
                <p style="margin-top: 1rem; font-size: 1.1rem; color: #dbeafe;">
                    Our platform has helped millions of people understand their health concerns
                </p>
                <div style="display: flex; flex-wrap: wrap; gap: 2rem; margin-top: 2rem; justify-content: center;">
                    <div style="text-align: center;">
                        <h3 style="font-size: 1.8rem; font-weight: bold;">5M+</h3>
                        <p>Health assessments</p>
                    </div>
                    <div style="text-align: center;">
                        <h3 style="font-size: 1.8rem; font-weight: bold;">200+</h3>
                        <p>Countries served</p>
                    </div>
                    <div style="text-align: center;">
                        <h3 style="font-size: 1.8rem; font-weight: bold;">98%</h3>
                        <p>Satisfaction rate</p>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    # ---------- Reviews Section ----------
    st.markdown("""
        <div style="padding: 4rem 1rem; background-color: #f0f4ff;">
            <div style="max-width: 1000px; margin: auto; text-align: center;">
                <h2 style="color: #2563eb; text-transform: uppercase; font-weight: 600;">Testimonials</h2>
                <h3 style="font-size: 2rem; font-weight: 800; margin-top: 0.5rem;">What our users are saying</h3>
                <div style="margin-top: 2rem; display: flex; flex-wrap: wrap; gap: 2rem; justify-content: center;">
                    <div style="background: white; padding: 2rem; border-radius: 1rem; width: 300px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                        <p style="color: #374151;">"I described my symptoms and within seconds got a detailed, helpful explanation. Amazing!"</p>
                        <p style="margin-top: 1rem; font-weight: 600; color: #1e3a8a;">— Sarah M.</p>
                    </div>
                    <div style="background: white; padding: 2rem; border-radius: 1rem; width: 300px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                        <p style="color: #374151;">"I used this tool late at night when clinics were closed. It really calmed my anxiety."</p>
                        <p style="margin-top: 1rem; font-weight: 600; color: #1e3a8a;">— Daniel K.</p>
                    </div>
                    <div style="background: white; padding: 2rem; border-radius: 1rem; width: 300px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                        <p style="color: #374151;">"Highly recommend to anyone looking for trustworthy symptom guidance. 10/10."</p>
                        <p style="margin-top: 1rem; font-weight: 600; color: #1e3a8a;">— Priya R.</p>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ---------- Contact Us Section ----------
    st.markdown("""
        <div style="padding: 4rem 1rem; background-color: #1e40af; color: white;">
            <div style="max-width: 800px; margin: auto; text-align: center;">
                <h2 style="font-size: 2rem; font-weight: 800;">Have Questions? Get in Touch!</h2>
                <p style="margin-top: 1rem; color: #dbeafe;">We're here to help with anything you need — feedback, support, or partnerships.</p>
                <form style="margin-top: 2rem; display: flex; flex-direction: column; gap: 1rem;">
                    <input type="text" placeholder="Your Name" style="padding: 0.75rem; border-radius: 0.5rem; border: none; width: 100%; max-width: 500px; margin: auto;" />
                    <input type="email" placeholder="Your Email" style="padding: 0.75rem; border-radius: 0.5rem; border: none; width: 100%; max-width: 500px; margin: auto;" />
                    <textarea placeholder="Your Message" rows="4" style="padding: 0.75rem; border-radius: 0.5rem; border: none; width: 100%; max-width: 500px; margin: auto;"></textarea>
                    <button type="submit" style="background: white; color: #1e40af; padding: 0.75rem 1.5rem; font-weight: bold; border: none; border-radius: 0.5rem; max-width: 200px; margin: auto;">Send Message</button>
                </form>
            </div>
        </div>
    """, unsafe_allow_html=True)

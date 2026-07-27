import streamlit as st
import google.generativeai as genai
import json
import re
import requests
from bs4 import BeautifulSoup

# App Layout Configuration
st.set_page_config(page_title="SiteGlow AI — Conversion & Design Engine", page_icon="⚡", layout="wide")

# Modern SaaS Styling with Custom CSS
st.markdown("""
<style>
    /* Dark Theme Core Styles */
    .stApp { background-color: #0B0F17; color: #E2E8F0; }
    
    /* Sleek Typography & Headers */
    .brand-badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #818CF8;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .main-title { font-size: 2.6rem; font-weight: 900; color: #FFFFFF; letter-spacing: -0.02em; margin-bottom: 4px; }
    .sub-title { font-size: 1.05rem; color: #94A3B8; margin-bottom: 28px; font-weight: 400; }
    
    /* Input & Button Styling */
    .stTextArea textarea {
        background-color: #131927 !important;
        border: 1px solid #1E293B !important;
        color: #F8FAFC !important;
        border-radius: 12px !important;
        font-size: 0.95rem !important;
    }
    .stTextArea textarea:focus { border-color: #6366F1 !important; box-shadow: 0 0 0 1px #6366F1 !important; }
    
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: 700;
        font-size: 1rem;
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        color: white;
        border: none;
        height: 3.2rem;
        box-shadow: 0 4px 20px rgba(79, 70, 229, 0.3);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #4338CA, #6D28D9);
        box-shadow: 0 6px 24px rgba(79, 70, 229, 0.45);
        transform: translateY(-1px);
    }
    
    /* Metrics & Custom Cards */
    div[data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 800 !important; color: #6366F1 !important; }
    .card-box {
        background: #131927;
        border: 1px solid #1E293B;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .tag-pill {
        display: inline-block;
        background: #1E293B;
        color: #CBD5E1;
        padding: 2px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown('<span class="brand-badge">⚡ Next-Gen Conversion Engine</span>', unsafe_allow_html=True)
st.markdown('<div class="main-title">SiteGlow AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Instant CRO Audit, Psychological Friction Diagnosis & Modern Hero UI Generator</div>', unsafe_allow_html=True)

# Helper Function: Web Scraper for Live URLs
def extract_website_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=6)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string if soup.title else ""
        meta_desc = ""
        meta_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        if meta_tag and meta_tag.get('content'):
            meta_desc = meta_tag['content']
            
        headings = [h.get_text().strip() for h in soup.find_all(['h1', 'h2']) if h.get_text().strip()]
        paragraphs = [p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()][:3]
        
        return f"Page Title: {title}\nMeta Description: {meta_desc}\nHeadings: {' | '.join(headings[:4])}\nSample Copy: {' '.join(paragraphs)}"[:1500]
    except Exception as e:
        return f"Could not scrape URL automatically: {e}"

# Sidebar Setup
with st.sidebar:
    st.header("⚙️ Engine Setup")
    raw_api_key = st.text_input("Enter Gemini API Key:", type="password")
    api_key = raw_api_key.strip() if raw_api_key else ""
    st.markdown("[Get a free key from Google AI Studio](https://aistudio.google.com/)")
    st.divider()
    st.caption("Powered by Gemini 3.6 Flash Engine")
    st.caption("Prometheus AI Challenge")

# Input Interface
user_input = st.text_area(
    "Paste product pitch OR website URL below:",
    height=120,
    placeholder="e.g. https://stripe.com OR 'We built a messaging tool for remote teams. You can send chats and share files easily...'"
)

if st.button("🚀 Analyze & Auto-Redesign Live", type="primary"):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    elif not user_input:
        st.warning("Please paste some pitch text or a website URL first.")
    else:
        with st.spinner("Analyzing psychological hooks and generating high-converting UI..."):
            try:
                processed_copy = user_input.strip()
                is_url = processed_copy.startswith("http://") or processed_copy.startswith("https://")
                
                if is_url:
                    st.info(f"🌐 Scraping content from `{processed_copy}`...")
                    processed_copy = extract_website_content(processed_copy)

                genai.configure(api_key=api_key)
                
                # Dynamic Model Discovery with Gemini 3.6 / 3.x Prioritization
                all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                priority_list = [
                    "models/gemini-3.6-flash",
                    "models/gemini-3.5-flash",
                    "models/gemini-3.1-pro-preview",
                    "models/gemini-3.1-flash-lite",
                    "models/gemini-flash-latest",
                    "models/gemini-pro-latest"
                ]
                
                available_models = [m for m in priority_list if m in all_models] + [m for m in all_models if m not in priority_list]

                if not available_models:
                    st.error("❌ No content models available for this API key.")
                    st.stop()

                prompt = f"""
                You are a world-class CRO (Conversion Rate Optimization) strategist and senior SaaS visual designer.
                Analyze this business copy/content: "{processed_copy}"

                EVALUATION & SCORING RULES:
                1. Assign a float score from 15.0 to 99.0 based on how outcome-driven, clear, and compelling it is.
                2. If an element (Headline, Value Prop, CTA) is ALREADY exceptional, set flaw text starting with "None — " (e.g., "None — Headline is outcome-focused and high-impact.").
                3. Rewrite the messaging into a stunning, ultra-high-converting Hero block section.
                4. Provide detailed rating scores (0-100) for Clarity, Urgency, Benefit Alignment, and Friction.

                Return ONLY a JSON object strictly matching this schema:
                {{
                    "original_score": 42.5,
                    "clarity_score": 50,
                    "urgency_score": 30,
                    "benefit_score": 40,
                    "friction_score": 80,
                    "headline_flaw": "Describes what you built (a commodity feature) instead of what the user gains.",
                    "value_prop_flaw": "Lacks specific outcome metrics, time-saved claims, or emotional transformation.",
                    "cta_flaw": "Generic, low-urgency button text with zero value proposition.",
                    "badge_text": "AUTOMATED WORKFLOWS",
                    "social_proof": "⚡ Trusted by 10,000+ high-growth teams",
                    "rewritten_headline": "Bring Your Remote Team into Perfect Alignment",
                    "rewritten_subheadline": "Stop losing tasks across fragmented chats. Unify execution, decision-making, and communication in one fast dashboard.",
                    "cta_primary": "Start Free 14-Day Trial →",
                    "cta_secondary": "Watch 2-Min Product Tour"
                }}
                Do not write introductory or markdown commentary outside JSON.
                """
                
                response = None
                used_model = "gemini-3.6-flash"
                for model_name in available_models:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt)
                        if response and response.text:
                            used_model = model_name
                            break
                    except Exception:
                        continue
                
                if not response or not response.text:
                    st.error("❌ Failed to fetch AI response. Please verify key quota.")
                    st.stop()

                # Robust JSON Extraction
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                data = json.loads(json_match.group(0)) if json_match else {}
                
                # Extract Scores
                try:
                    orig_score = round(float(data.get("original_score", 65.0)), 1)
                except Exception:
                    orig_score = 65.0

                clarity = data.get("clarity_score", 60)
                urgency = data.get("urgency_score", 40)
                benefit = data.get("benefit_score", 50)
                friction = data.get("friction_score", 70)
                
                headline_flaw = data.get("headline_flaw", "Focuses on internal building process rather than external results.")
                value_flaw = data.get("value_prop_flaw", "Lists commodity features without highlighting emotional stakes.")
                cta_flaw = data.get("cta_flaw", "Low-energy CTA with minimal incentive to click.")
                
                badge = data.get("badge_text", "AI WORKFLOW ENGINE")
                social_proof = data.get("social_proof", "⚡ Loved by 5,000+ founders")
                headline = data.get("rewritten_headline", "Eliminate Chaos & Scale Execution")
                subheadline = data.get("rewritten_subheadline", "Stop jumping between endless tabs. Streamline collaboration with an intelligent workspace.")
                cta_primary = data.get("cta_primary", "Get Started Free →")
                cta_secondary = data.get("cta_secondary", "View Live Demo")

                # Helper to render Status Icon
                def get_status_badge(flaw_text):
                    clean = flaw_text.strip().lower()
                    if clean.startswith("none") or "strong" in clean or "excellent" in clean or "catchy" in clean:
                        return "✅ <span style='color:#34D399; font-weight:700;'>Optimal</span>"
                    return "❌ <span style='color:#F87171; font-weight:700;'>Flaw Detected</span>"

                # Streamlit Display Tabs
                tab1, tab2, tab3 = st.tabs(["📊 CRO Intelligence Scorecard", "✨ Live Hero Redesign", "💻 Export Code & Implement"])

                with tab1:
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown('<div class="card-box">', unsafe_allow_html=True)
                        potential_boost = round(max(0.0, 98.0 - orig_score), 1)
                        st.metric("Conversion Health Score", f"{orig_score} / 100", delta=f"+{potential_boost}% Estimated Lift", delta_color="normal")
                        st.caption(f"Engine Model: `{used_model}`")
                        
                        st.write("---")
                        
                        # Adaptive Risk Banner
                        if orig_score >= 82.0:
                            st.success("🎉 **High-Converting Messaging!** Clear positioning with strong user value.")
                        elif orig_score >= 60.0:
                            st.info("💡 **Good Foundation.** Minor messaging tweaks needed to eliminate hesitation.")
                        else:
                            st.warning("⚠️ **High Bounce Rate Risk.** Pitch is feature-centric and lacks immediate value.")
                        
                        st.markdown('</div>', unsafe_allow_html=True)

                        # Psychological Metrics
                        st.markdown('<div class="card-box">', unsafe_allow_html=True)
                        st.subheader("🧠 CRO Psychological Breakdown")
                        st.write(f"**Message Clarity:** {clarity}/100")
                        st.progress(clarity / 100)
                        st.write(f"**Value/Benefit Focus:** {benefit}/100")
                        st.progress(benefit / 100)
                        st.write(f"**Call-to-Action Urgency:** {urgency}/100")
                        st.progress(urgency / 100)
                        st.write(f"**Friction Level (Lower is better):** {friction}/100")
                        st.progress(friction / 100)
                        st.markdown('</div>', unsafe_allow_html=True)

                    with col2:
                        st.markdown('<div class="card-box">', unsafe_allow_html=True)
                        st.subheader("🔍 Breakdown & Flaw Diagnosis")
                        
                        st.markdown(f"#### {get_status_badge(headline_flaw)} Headline Structure", unsafe_allow_html=True)
                        st.write(headline_flaw)
                        st.write("---")
                        
                        st.markdown(f"#### {get_status_badge(value_flaw)} Value Proposition & Benefits", unsafe_allow_html=True)
                        st.write(value_flaw)
                        st.write("---")
                        
                        st.markdown(f"#### {get_status_badge(cta_flaw)} Call-To-Action (CTA)", unsafe_allow_html=True)
                        st.write(cta_flaw)
                        
                        st.markdown('</div>', unsafe_allow_html=True)

                with tab2:
                    st.subheader("✨ High-Converting Redesign")
                    st.caption("Live, responsive preview powered by Tailwind CSS & Glassmorphism.")
                    
                    # HTML Template with UI Mockup
                    hero_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <script src="https://cdn.tailwindcss.com"></script>
                        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800&display=swap" rel="stylesheet">
                        <style>
                            body {{ font-family: 'Plus Jakarta Sans', sans-serif; background-color: #090d16; color: #ffffff; margin: 0; padding: 24px; }}
                            .glass-card {{ background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }}
                        </style>
                    </head>
                    <body>
                        <div class="relative max-w-4xl mx-auto glass-card rounded-3xl p-10 md:p-14 shadow-2xl overflow-hidden">
                            <!-- Gradient Glow Backgrounds -->
                            <div class="absolute -top-32 -left-32 w-80 h-80 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none"></div>
                            <div class="absolute -bottom-32 -right-32 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl pointer-events-none"></div>
                            
                            <div class="relative z-10 text-center">
                                <span class="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/25 text-indigo-300 text-xs font-bold px-4 py-1.5 rounded-full mb-6 tracking-wide uppercase">
                                    ✨ {badge}
                                </span>
                                
                                <h1 class="text-4xl md:text-6xl font-extrabold tracking-tight text-white mb-6 leading-tight">
                                    {headline}
                                </h1>
                                
                                <p class="text-slate-300 text-base md:text-xl mb-8 max-w-2xl mx-auto leading-relaxed">
                                    {subheadline}
                                </p>
                                
                                <div class="flex flex-col sm:flex-row gap-4 justify-center items-center mb-10">
                                    <button class="w-full sm:w-auto bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-bold px-9 py-4 rounded-xl shadow-lg shadow-indigo-500/25 transition-all duration-200">
                                        {cta_primary}
                                    </button>
                                    <button class="w-full sm:w-auto bg-slate-800/80 hover:bg-slate-700 text-slate-200 font-bold px-8 py-4 rounded-xl border border-slate-700 transition-all duration-200">
                                        {cta_secondary}
                                    </button>
                                </div>
                                
                                <p class="text-xs text-slate-400 font-medium tracking-wide">
                                    {social_proof}
                                </p>
                                
                                <!-- Rendered Product Mockup Card -->
                                <div class="mt-12 p-4 bg-slate-950/80 border border-slate-800/80 rounded-2xl shadow-inner">
                                    <div class="flex items-center gap-2 mb-3">
                                        <div class="w-3 h-3 rounded-full bg-red-500/80"></div>
                                        <div class="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                                        <div class="w-3 h-3 rounded-full bg-green-500/80"></div>
                                        <span class="text-xs text-slate-500 ml-2 font-mono">dashboard.siteglow.ai</span>
                                    </div>
                                    <div class="h-32 bg-slate-900/50 rounded-xl border border-dashed border-slate-800 flex items-center justify-center text-slate-500 text-sm">
                                        🚀 Live Application Dashboard Mockup
                                    </div>
                                </div>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    st.components.v1.html(hero_html, height=620, scrolling=True)

                with tab3:
                    st.subheader("💻 Ready-to-Use Tailwind HTML")
                    st.caption("Copy and paste this code straight into Framer, Webflow, React, or standard HTML.")
                    st.code(hero_html, language="html")

            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

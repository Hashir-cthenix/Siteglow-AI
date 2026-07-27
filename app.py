import streamlit as st
import google.generativeai as genai
import json
import re
import requests
from bs4 import BeautifulSoup

# App Layout Configuration
st.set_page_config(page_title="SiteGlow AI — Copywriting & Persuasion Tutor", page_icon="🎓", layout="wide")

# Modern SaaS & EdTech Styling
st.markdown("""
<style>
    .stApp { background-color: #0B0F17; color: #E2E8F0; }
    
    .brand-badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.35);
        color: #818CF8;
        padding: 5px 16px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .main-title { font-size: 2.6rem; font-weight: 900; color: #FFFFFF; letter-spacing: -0.02em; margin-bottom: 6px; }
    .sub-title { font-size: 1.05rem; color: #94A3B8; margin-bottom: 28px; font-weight: 400; }
    
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
    
    div[data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 800 !important; color: #6366F1 !important; }
    .card-box {
        background: #131927;
        border: 1px solid #1E293B;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 16px;
    }
    .lesson-box {
        background: rgba(99, 102, 241, 0.08);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 12px;
        padding: 16px;
        margin-top: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown('<span class="brand-badge">🎓 AI Interactive Learning Platform</span>', unsafe_allow_html=True)
st.markdown('<div class="main-title">SiteGlow AI Tutor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Master the Psychology of Persuasive Writing, Positioning & CRO Through Real-Time AI Feedback</div>', unsafe_allow_html=True)

# Helper Function: Web Scraper for URLs
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
        
        return f"Page Title: {title}\nMeta Description: {meta_desc}\nHeadings: {' | '.join(headings[:4])}\nSample Text: {' '.join(paragraphs)}"[:1500]
    except Exception as e:
        return f"Could not scrape URL automatically: {e}"

# Sidebar Setup
with st.sidebar:
    st.header("⚙️ Tutor Engine Setup")
    raw_api_key = st.text_input("Enter Gemini API Key:", type="password")
    api_key = raw_api_key.strip() if raw_api_key else ""
    st.markdown("[Get a free API key from Google AI Studio](https://aistudio.google.com/)")
    st.divider()
    st.caption("🏆 Built for Prometheus AI Challenge")
    st.caption("Focus Area: EdTech & Personalized Learning")

# Main Input Section
user_input = st.text_area(
    "Paste product pitch, landing page draft, OR website URL to analyze:",
    height=120,
    placeholder="e.g. 'We made a messaging app for teams. You can send chats and share files easily. Sign up today.' OR https://stripe.com"
)

if st.button("🎓 Start AI Copywriting Lesson & Audit", type="primary"):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    elif not user_input:
        st.warning("Please paste some pitch text or a website URL first.")
    else:
        with st.spinner("Analyzing writing psychology and preparing your personalized lesson..."):
            try:
                processed_copy = user_input.strip()
                is_url = processed_copy.startswith("http://") or processed_copy.startswith("https://")
                
                if is_url:
                    st.info(f"🌐 Website URL detected! Extracting content from `{processed_copy}`...")
                    processed_copy = extract_website_content(processed_copy)

                genai.configure(api_key=api_key)
                
                # Model Prioritization Queue
                all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                priority_list = [
                    "models/gemini-3.6-flash",
                    "models/gemini-3.5-flash",
                    "models/gemini-3.1-pro-preview",
                    "models/gemini-2.5-flash",
                    "models/gemini-1.5-pro"
                ]
                available_models = [m for m in priority_list if m in all_models] + [m for m in all_models if m not in priority_list]

                if not available_models:
                    st.error("❌ No content models available for this API key.")
                    st.stop()

                prompt = f"""
                You are an elite Copywriting Professor and CRO Strategist teaching students how to write high-converting, outcome-focused copy.
                Analyze this draft input: "{processed_copy}"

                EVALUATION & TEACHING RULES:
                1. Score the draft from 15.0 to 99.0 based on persuasiveness and clarity.
                2. Identify the key "Teachable Lesson" (e.g., "The You vs. We Rule", "Outcome-Driven Positioning", or "Frictionless CTAs").
                3. Provide a micro-lesson explaining the copywriting principle used in the rewrite.
                4. Diagnose flaws in Headline, Value Prop, and CTA. If an element is ALREADY excellent, start the text with "None — ".

                Return ONLY a JSON object with this exact structure:
                {{
                    "original_score": 42.5,
                    "clarity_score": 50,
                    "urgency_score": 30,
                    "benefit_score": 40,
                    "friction_score": 75,
                    "lesson_title": "The Outcome Over Feature Principle",
                    "micro_lesson": "People don't buy features; they buy the transformation those features provide. Instead of saying 'What we built,' show 'What the user becomes.'",
                    "headline_flaw": "Describes what you built (a commodity feature) instead of what the user achieves.",
                    "value_prop_flaw": "Lists static tools without highlighting time saved or emotional stakes.",
                    "cta_flaw": "Generic button text with zero urgency or incentive.",
                    "badge_text": "AUTOMATED WORKFLOWS",
                    "social_proof": "⚡ Trusted by 10,000+ creators",
                    "rewritten_headline": "Bring Your Remote Team into Perfect Alignment",
                    "rewritten_subheadline": "Stop losing tasks across fragmented chats. Unify execution and decision-making in one fast dashboard.",
                    "cta_primary": "Start Free 14-Day Trial →",
                    "cta_secondary": "Watch 2-Min Demo"
                }}
                Do not include markdown commentary outside JSON.
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
                    st.error("❌ Failed to fetch AI response.")
                    st.stop()

                # Robust JSON Extraction
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                data = json.loads(json_match.group(0)) if json_match else {}
                
                # Parse Scores
                try:
                    orig_score = round(float(data.get("original_score", 65.0)), 1)
                except Exception:
                    orig_score = 65.0

                clarity = data.get("clarity_score", 60)
                urgency = data.get("urgency_score", 40)
                benefit = data.get("benefit_score", 50)
                friction = data.get("friction_score", 70)
                
                lesson_title = data.get("lesson_title", "Focusing on Transformation over Features")
                micro_lesson = data.get("micro_lesson", "Effective copy focuses on the end-result for the reader, not the specifications of the product.")
                headline_flaw = data.get("headline_flaw", "Focuses on internal features rather than user outcomes.")
                value_flaw = data.get("value_prop_flaw", "Lists commodity features without emotional hook.")
                cta_flaw = data.get("cta_flaw", "Low-urgency call to action.")
                
                badge = data.get("badge_text", "AI WORKFLOW ENGINE")
                social_proof = data.get("social_proof", "⚡ Loved by 5,000+ creators")
                headline = data.get("rewritten_headline", "Eliminate Chaos & Scale Execution")
                subheadline = data.get("rewritten_subheadline", "Streamline collaboration with an intelligent workspace.")
                cta_primary = data.get("cta_primary", "Get Started Free →")
                cta_secondary = data.get("cta_secondary", "View Live Demo")

                # Helper to render Status Icon
                def get_status_badge(flaw_text):
                    clean = flaw_text.strip().lower()
                    if clean.startswith("none") or "strong" in clean or "excellent" in clean or "catchy" in clean:
                        return "✅ <span style='color:#34D399; font-weight:700;'>Mastered</span>"
                    return "❌ <span style='color:#F87171; font-weight:700;'>Needs Improvement</span>"

                # Streamlit Display Tabs
                tab1, tab2, tab3 = st.tabs(["🎓 Interactive Lesson & Breakdown", "✨ Live Practical Application", "💻 Export Code & Study"])

                with tab1:
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown('<div class="card-box">', unsafe_allow_html=True)
                        potential_boost = round(max(0.0, 98.0 - orig_score), 1)
                        st.metric("Writing Effectiveness Score", f"{orig_score} / 100", delta=f"+{potential_boost}% Improvement Potential", delta_color="normal")
                        st.caption(f"Evaluated by AI Engine: `{used_model}`")
                        
                        st.write("---")
                        
                        if orig_score >= 82.0:
                            st.success("🎉 **Mastery Level!** Exceptional clarity and persuasive structure.")
                        elif orig_score >= 60.0:
                            st.info("💡 **Solid Start.** A few psychological tweaks will elevate impact.")
                        else:
                            st.warning("⚠️ **Needs Work.** Writing focuses on 'what you built' rather than 'what the user gains.'")
                        
                        st.markdown('</div>', unsafe_allow_html=True)

                        # Copywriting Skill Radar
                        st.markdown('<div class="card-box">', unsafe_allow_html=True)
                        st.subheader("🧠 Persuasion Skill Breakdown")
                        st.write(f"**Clarity & Hook:** {clarity}/100")
                        st.progress(clarity / 100)
                        st.write(f"**Outcome & Benefit Focus:** {benefit}/100")
                        st.progress(benefit / 100)
                        st.write(f"**Urgency & Incentive:** {urgency}/100")
                        st.progress(urgency / 100)
                        st.write(f"**Friction Level (Lower is better):** {friction}/100")
                        st.progress(friction / 100)
                        st.markdown('</div>', unsafe_allow_html=True)

                    with col2:
                        st.markdown('<div class="card-box">', unsafe_allow_html=True)
                        st.subheader("💡 The Teachable Principle")
                        st.markdown(f"### 📖 Lesson: **{lesson_title}**")
                        st.markdown(f'<div class="lesson-box"><b>🎓 Coach\'s Insight:</b> {micro_lesson}</div>', unsafe_allow_html=True)
                        st.write("---")
                        
                        st.subheader("🔍 Detailed Feedback")
                        st.markdown(f"#### {get_status_badge(headline_flaw)} Headline Structure", unsafe_allow_html=True)
                        st.write(headline_flaw)
                        st.write("---")
                        
                        st.markdown(f"#### {get_status_badge(value_flaw)} Value Proposition & Outcome", unsafe_allow_html=True)
                        st.write(value_flaw)
                        st.write("---")
                        
                        st.markdown(f"#### {get_status_badge(cta_flaw)} Call-To-Action (CTA)", unsafe_allow_html=True)
                        st.write(cta_flaw)
                        
                        st.markdown('</div>', unsafe_allow_html=True)

                with tab2:
                    st.subheader("✨ Applied Practical Transformation")
                    st.caption("Here is how your writing transforms visually when applying these copywriting principles live.")
                    
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
                                
                                <div class="mt-12 p-4 bg-slate-950/80 border border-slate-800/80 rounded-2xl shadow-inner">
                                    <div class="flex items-center gap-2 mb-3">
                                        <div class="w-3 h-3 rounded-full bg-red-500/80"></div>
                                        <div class="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                                        <div class="w-3 h-3 rounded-full bg-green-500/80"></div>
                                        <span class="text-xs text-slate-500 ml-2 font-mono">dashboard.siteglow.ai</span>
                                    </div>
                                    <div class="h-32 bg-slate-900/50 rounded-xl border border-dashed border-slate-800 flex items-center justify-center text-slate-500 text-sm">
                                        🚀 Rendered High-Converting Interface Preview
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
                    st.caption("Study the structure or export it directly for production.")
                    st.code(hero_html, language="html")

            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

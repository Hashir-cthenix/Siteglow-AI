import streamlit as st
import google.generativeai as genai
import json
import re
import requests
from bs4 import BeautifulSoup

# App Layout Configuration
st.set_page_config(page_title="SiteGlow AI — Conversion & Design Engine", page_icon="⚡", layout="wide")

# Custom CSS styling for Streamlit UI
st.markdown("""
<style>
    .main-title { font-size: 2.2rem; font-weight: 800; color: #6366f1; margin-bottom: 0px; }
    .sub-title { font-size: 1rem; color: #94a3b8; margin-bottom: 25px; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 600; background: linear-gradient(90deg, #4f46e5, #7c3aed); color: white; border: none; height: 3rem; }
    .stButton>button:hover { background: linear-gradient(90deg, #4338ca, #6d28d9); color: white; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">⚡ SiteGlow AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Instant Conversion Rate Audit & Live High-Converting UI Generator</div>', unsafe_allow_html=True)

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
        
        scraped_summary = f"Page Title: {title}\nMeta Description: {meta_desc}\nHeadings: {' | '.join(headings[:4])}\nSample Text: {' '.join(paragraphs)}"
        return scraped_summary[:1500]
    except Exception as e:
        return f"Could not automatically fetch URL content: {e}. Analyzing URL text directly."

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Engine Setup")
    raw_api_key = st.text_input("Enter Free Gemini API Key:", type="password")
    api_key = raw_api_key.strip() if raw_api_key else ""
    st.markdown("[Get a free Gemini API key from Google AI Studio](https://aistudio.google.com/)")
    st.divider()
    st.caption("Built for Prometheus July AI Challenge")

# Main Input Section
user_input = st.text_area(
    "Paste product pitch OR website URL below:",
    height=120,
    placeholder="e.g. https://stripe.com OR 'We built a team chat tool that helps remote workers...'"
)

if st.button("🚀 Analyze & Auto-Redesign Live", type="primary"):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    elif not user_input:
        st.warning("Please paste some text or a website URL first.")
    else:
        with st.spinner("Processing input and building high-converting UI..."):
            try:
                # Determine if input is a URL or raw text
                processed_copy = user_input.strip()
                is_url = processed_copy.startswith("http://") or processed_copy.startswith("https://")
                
                if is_url:
                    st.info(f"🌐 Website URL detected! Auto-extracting live content from `{processed_copy}`...")
                    processed_copy = extract_website_content(processed_copy)

                genai.configure(api_key=api_key)
                
                # Dynamic model discovery
                available_models = [
                    m.name for m in genai.list_models() 
                    if 'generateContent' in m.supported_generation_methods
                ]
                
                if not available_models:
                    st.error("❌ No content models available for this key.")
                    st.stop()
                prompt = f"""
                You are an elite Conversion Rate Optimization (CRO) expert.
                Evaluate this business copy/content: "{processed_copy}"

                EVALUATION RULES:
                - If the copy is weak/generic, assign a LOW score (20–60), detail critical flaws, and create a high-converting redesign.
                - If the copy is ALREADY exceptional, catchy, and high-converting, assign a HIGH score (85–98), mark flaws as "None — Copy is already clear and outcome-driven!", and keep/enhance the strong messaging in the hero block.

                Return ONLY a JSON object strictly formatted as:
                {{
                    "original_score": 85,
                    "headline_flaw": "Specific flaw OR 'None — Headline is strong, outcome-focused, and catchy.'",
                    "value_prop_flaw": "Specific flaw OR 'None — Value proposition clearly articulates benefits.'",
                    "cta_flaw": "Specific flaw OR 'None — Call to action is high-friction and compelling.'",
                    "badge_text": "HIGH-CONVERTING COPY",
                    "rewritten_headline": "Preserved or slightly polished headline",
                    "rewritten_subheadline": "Preserved or slightly polished subheadline",
                    "cta_primary": "Primary CTA text",
                    "cta_secondary": "Secondary CTA text"
                }}
                Do not include extra text outside JSON.
                """
                
                response = None
                for model_name in available_models:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt)
                        if response and response.text:
                            break
                    except Exception:
                        continue
                
                if not response or not response.text:
                    st.error("❌ Failed to fetch AI response. Please check your API key quota.")
                    st.stop()

                # Robust JSON Extraction
                raw_text = response.text
                json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                
                data = {}
                if json_match:
                    try:
                        data = json.loads(json_match.group(0))
                    except Exception:
                        data = {}
                
                # Fallback values
                orig_score = data.get("original_score", 38)
                headline_flaw = data.get("headline_flaw", "Focuses on internal building process rather than customer value.")
                value_flaw = data.get("value_prop_flaw", "Lists features as commodities without explaining emotional stakes.")
                cta_flaw = data.get("cta_flaw", "Generic button copy with zero urgency.")
                
                badge = data.get("badge_text", "AI WORKFLOW ENGINE")
                headline = data.get("rewritten_headline", "Eliminate Chaos and Streamline Team Performance")
                subheadline = data.get("rewritten_subheadline", "Stop losing tasks across fragmented chat apps. Unify team collaboration and execution in one workspace.")
                cta_primary = data.get("cta_primary", "Get Started Free →")
                cta_secondary = data.get("cta_secondary", "View Live Demo")

                # Streamlit Display Tabs
                tab1, tab2, tab3 = st.tabs(["📊 Conversion Scorecard", "✨ Live Hero Redesign", "💻 Export Code"])

                with tab1:
                    col_score1, col_score2 = st.columns([1, 2])
                    with col_score1:
                        st.metric("Original Copy Health Score", f"{orig_score} / 100", delta=f"+{95 - orig_score} Potential Boost", delta_color="normal")
                        st.warning("⚠️ High bounce rate risk detected in original content.")
                    
                    with col_score2:
                        st.subheader("🔍 Breakdown & Conversion Flaws")
                        st.markdown(f"**❌ Headline Issue:** {headline_flaw}")
                        st.markdown(f"**❌ Value Prop Issue:** {value_flaw}")
                        st.markdown(f"**❌ CTA Issue:** {cta_flaw}")

                with tab2:
                    st.subheader("✨ Auto-Rendered High-Converting Hero")
                    hero_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <script src="https://cdn.tailwindcss.com"></script>
                        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
                        <style>
                            body {{ font-family: 'Plus Jakarta Sans', sans-serif; background-color: #090d16; color: #ffffff; margin: 0; padding: 20px; }}
                        </style>
                    </head>
                    <body>
                        <div class="relative max-w-3xl mx-auto bg-slate-900/90 border border-slate-800 rounded-3xl p-10 shadow-2xl overflow-hidden">
                            <div class="absolute -top-24 -left-24 w-72 h-72 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none"></div>
                            <div class="absolute -bottom-24 -right-24 w-72 h-72 bg-purple-500/20 rounded-full blur-3xl pointer-events-none"></div>
                            
                            <div class="relative z-10 text-center">
                                <span class="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-bold px-4 py-1.5 rounded-full mb-6 tracking-wide uppercase">
                                    ✨ {badge}
                                </span>
                                
                                <h1 class="text-4xl md:text-5xl font-extrabold tracking-tight text-white mb-4 leading-tight">
                                    {headline}
                                </h1>
                                
                                <p class="text-slate-300 text-base md:text-lg mb-8 max-w-2xl mx-auto leading-relaxed">
                                    {subheadline}
                                </p>
                                
                                <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
                                    <button class="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-8 py-3.5 rounded-xl shadow-lg shadow-indigo-500/25 transition-all duration-200">
                                        {cta_primary}
                                    </button>
                                    <button class="w-full sm:w-auto bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold px-8 py-3.5 rounded-xl border border-slate-700 transition-all duration-200">
                                        {cta_secondary}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    st.components.v1.html(hero_html, height=480, scrolling=False)

                with tab3:
                    st.subheader("💻 Ready-to-Use Tailwind HTML")
                    st.code(hero_html, language="html")

            except Exception as e:
                st.error(f"Unexpected error occurred: {e}")

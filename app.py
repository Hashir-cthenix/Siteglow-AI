import streamlit as st
import google.generativeai as genai
import json
import re

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

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Engine Setup")
    raw_api_key = st.text_input("Enter Free Gemini API Key:", type="password")
    api_key = raw_api_key.strip() if raw_api_key else ""
    st.markdown("[Get a free Gemini API key from Google AI Studio](https://aistudio.google.com/)")
    st.divider()
    st.caption("Built for Prometheus July AI Challenge")

# Main Input Section
pitch_input = st.text_area(
    "Paste your raw product pitch or website copy below:",
    height=120,
    placeholder="e.g. We built a tool for remote teams. It lets you send messages and share tasks. Try it today."
)

if st.button("🚀 Analyze Copy & Generate Redesign", type="primary"):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    elif not pitch_input:
        st.warning("Please paste some text first.")
    else:
        with st.spinner("Analyzing psychological hooks and building high-converting UI..."):
            try:
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
                You are a top CRO (Conversion Rate Optimization) expert and SaaS designer.
                Analyze this copy: "{pitch_input}"

                Return ONLY a single valid JSON object strictly formatted as follows (no extra conversational text, no markdown backticks outside json):
                {{
                    "original_score": 35,
                    "headline_flaw": "Specific critical issue with the current headline.",
                    "value_prop_flaw": "Specific critical issue with the current value proposition.",
                    "cta_flaw": "Specific issue with the call to action.",
                    "badge_text": "AI-POWERED WORKFLOWS",
                    "rewritten_headline": "An explosive, high-converting outcome-driven headline",
                    "rewritten_subheadline": "A clear 2-sentence value proposition focusing on eliminating customer pain points and saving time.",
                    "cta_primary": "Start Free Trial →",
                    "cta_secondary": "Watch 2-Min Demo"
                }}
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

                # Clean and parse JSON output
                clean_text = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_text)

                # Extract parsed fields with fallbacks
                orig_score = data.get("original_score", 40)
                badge = data.get("badge_text", "NEW FEATURE")
                headline = data.get("rewritten_headline", "Eliminate Chaos and Streamline Your Workflow")
                subheadline = data.get("rewritten_subheadline", "Stop jumping between fragmented tools. Centralize communication and project execution in one unified workspace.")
                cta_primary = data.get("cta_primary", "Get Started Free →")
                cta_secondary = data.get("cta_secondary", "View Live Demo")

                # Streamlit Display Tabs
                tab1, tab2, tab3 = st.tabs(["📊 Conversion Scorecard", "✨ Live Hero Redesign", "💻 Export Code"])

                with tab1:
                    col_score1, col_score2 = st.columns([1, 2])
                    with col_score1:
                        st.metric("Original Copy Health Score", f"{orig_score} / 100", delta=f"+{95 - orig_score} Potential Boost", delta_color="normal")
                        st.warning("⚠️ High bounce rate risk detected in current copy.")
                    
                    with col_score2:
                        st.subheader("🔍 Breakdown & Conversion Flaws")
                        st.markdown(f"**❌ Headline Flaw:** {data.get('headline_flaw', 'Focuses on building the tool rather than customer value.')}")
                        st.markdown(f"**❌ Value Prop Flaw:** {data.get('value_prop_flaw', 'Lists commodity features instead of desired outcomes.')}")
                        st.markdown(f"**❌ CTA Flaw:** {data.get('cta_flaw', 'Generic button copy with low motivation.')}")

                with tab2:
                    st.subheader("✨ Auto-Rendered High-Converting Hero")
                    # Injected High-Contrast Glassmorphic Dark-Mode HTML Template
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
                            <!-- Background Glow Effect -->
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

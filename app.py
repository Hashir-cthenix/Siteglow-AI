import streamlit as st
import google.generativeai as genai

# App Layout Configuration
st.set_page_config(page_title="SiteGlow AI", page_icon="⚡", layout="wide")

st.title("⚡ SiteGlow AI — Instant Conversion & Design Healer")
st.caption("Audit weak copy and auto-render high-converting Tailwind landing page components in seconds.")

# Sidebar for Free Gemini API Key
with st.sidebar:
    st.header("1. Configuration")
    raw_api_key = st.text_input("Enter Free Gemini API Key:", type="password")
    api_key = raw_api_key.strip() if raw_api_key else ""
    st.markdown("[Get a free Gemini API key from Google AI Studio](https://aistudio.google.com/)")

# Main Input Section
st.subheader("2. Input Landing Page Copy or Pitch")
pitch_input = st.text_area(
    "Paste product text below:",
    height=140,
    placeholder="e.g. We created an app that helps remote teams track tasks and share notes fast..."
)

if st.button("🚀 Audit Copy & Redesign Live", type="primary"):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    elif not pitch_input:
        st.warning("Please paste some text first.")
    else:
        with st.spinner("Connecting to Google Gemini AI..."):
            try:
                # 1. Configure API key with automatic whitespace cleanup
                genai.configure(api_key=api_key)
                
                # 2. Dynamically query Google for exact model names valid for YOUR key
                try:
                    available_models = [
                        m.name for m in genai.list_models() 
                        if 'generateContent' in m.supported_generation_methods
                    ]
                except Exception as auth_err:
                    st.error(f"❌ Invalid API Key or Authentication Error. Please check your key on Google AI Studio: {auth_err}")
                    st.stop()

                if not available_models:
                    st.error("❌ No content generation models available for this API Key. Try generating a new key on Google AI Studio.")
                    st.stop()

                prompt = f"""
                You are a world-class Conversion Rate Optimization (CRO) copywriter and UI designer.
                Analyze this product copy/pitch: "{pitch_input}"
                
                Respond in this strict structure:
                ### AUDIT & CONVERSION FLAWS
                - **Headline Issue:** [Explanation]
                - **Value Prop Issue:** [Explanation]
                - **CTA Issue:** [Explanation]
                
                ### ACTIONABLE FIXES
                - **Fix 1:** [Recommendation]
                - **Fix 2:** [Recommendation]
                
                ### HTML
                ```html
                <div class="bg-slate-900 text-white p-8 rounded-2xl max-w-2xl mx-auto shadow-2xl border border-slate-800 font-sans">
                    <span class="bg-indigo-500/10 text-indigo-400 text-xs font-semibold px-3 py-1 rounded-full border border-indigo-500/20">NEW RELEASE</span>
                    <h1 class="text-3xl font-extrabold mt-4 mb-2 tracking-tight text-white">[High Converting Rewritten Headline]</h1>
                    <p class="text-slate-400 text-sm mb-6">[Clear, sharp 2-sentence value proposition]</p>
                    <div class="flex gap-3">
                        <button class="bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm px-5 py-2.5 rounded-lg shadow-lg transition-all">Get Started Free →</button>
                        <button class="bg-slate-800 text-slate-300 font-medium text-sm px-5 py-2.5 rounded-lg border border-slate-700">View Demo</button>
                    </div>
                </div>
                ```
                Fill the HTML snippet with compelling rewritten content based on the user's pitch.
                """
                
                response = None
                used_model_name = None
                
                # 3. Loop through the exact model strings provided directly by Google's server
                for model_name in available_models:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt)
                        if response and response.text:
                            used_model_name = model_name
                            break
                    except Exception:
                        continue
                
                if not response or not response.text:
                    st.error("❌ Could not get a response from Google. Please check your AI Studio quota.")
                    st.stop()

                raw_output = response.text
                
                # Separate text analysis from HTML code block
                audit_text = raw_output.split("### HTML")[0] if "### HTML" in raw_output else raw_output
                html_code = ""
                if "```html" in raw_output:
                    html_code = raw_output.split("```html")[1].split("```")[0].strip()
                
                # Display side-by-side results
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("📊 Conversion Audit")
                    st.caption(f"Connected Model: `{used_model_name}`")
                    st.markdown(audit_text)
                    
                with col2:
                    st.subheader("✨ Auto-Rendered Hero Redesign")
                    if html_code:
                        full_preview = f"""
                        <!DOCTYPE html>
                        <html>
                        <head><script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script></head>
                        <body class="bg-slate-950 p-4">
                            {html_code}
                        </body>
                        </html>
                        """
                        st.components.v1.html(full_preview, height=480, scrolling=True)
                    else:
                        st.info("HTML output preview couldn't be parsed.")
            except Exception as e:
                st.error(f"Unexpected Error: {e}")

import streamlit as st
import google.generativeai as genai
import json
import re
import html as html_lib
import requests
from bs4 import BeautifulSoup
import time
import concurrent.futures

# ==============================================================================
# 1. APP CONFIGURATION & STYLING
# ==============================================================================
st.set_page_config(
    page_title="SiteGlow AI — Conversion Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Dark Glassmorphism Styling
st.markdown("""
<style>
    .stApp { 
        background-color: #090D16; 
        color: #E2E8F0; 
    }
    
    .brand-badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.4);
        color: #A5B4FC;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    
    .main-title { 
        font-size: 2.8rem; 
        font-weight: 900; 
        color: #FFFFFF; 
        letter-spacing: -0.03em; 
        margin-bottom: 6px; 
    }
    
    .sub-title { 
        font-size: 1.1rem; 
        color: #94A3B8; 
        margin-bottom: 28px; 
        font-weight: 500; 
        line-height: 1.5; 
    }
    
    .stTextArea textarea {
        background-color: #111827 !important;
        border: 1px solid #1F2937 !important;
        color: #F9FAFB !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    
    .stTextArea textarea:focus { 
        border-color: #6366F1 !important; 
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important; 
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        font-weight: 800;
        font-size: 1.05rem;
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        color: white;
        border: none;
        height: 3.4rem;
        box-shadow: 0 4px 20px rgba(79, 70, 229, 0.35);
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #4338CA, #6D28D9);
        box-shadow: 0 6px 24px rgba(79, 70, 229, 0.5);
        transform: translateY(-1px);
    }
    
    div[data-testid="stMetricValue"] { 
        font-size: 2.2rem !important; 
        font-weight: 900 !important; 
        color: #818CF8 !important; 
    }
    
    .card-box {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .card-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: #F3F4F6;
        margin-bottom: 14px;
        border-bottom: 1px solid #1F2937;
        padding-bottom: 8px;
    }
    
    .winner-badge {
        display: inline-block;
        background: linear-gradient(135deg, #059669, #10B981);
        color: #FFFFFF;
        padding: 8px 18px;
        border-radius: 20px;
        font-size: 1rem;
        font-weight: 800;
    }
    
    .loser-badge {
        display: inline-block;
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.4);
        color: #FCA5A5;
        padding: 8px 18px;
        border-radius: 20px;
        font-size: 1rem;
        font-weight: 800;
    }
    
    .site-label-blue {
        display: inline-block;
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(59, 130, 246, 0.4);
        color: #93C5FD;
        padding: 4px 14px;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 800;
        margin-bottom: 8px;
    }
    
    .site-label-red {
        display: inline-block;
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.4);
        color: #FCA5A5;
        padding: 4px 14px;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 800;
        margin-bottom: 8px;
    }
    
    .lesson-card {
        background: #111827;
        border: 1px solid #1F2937;
        border-left: 4px solid #6366F1;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }
    
    .lesson-title { 
        color: #A5B4FC; 
        font-weight: 800; 
        font-size: 1rem; 
        margin-bottom: 4px; 
    }
    
    .lesson-body { 
        color: #D1D5DB; 
        font-size: 0.92rem; 
        line-height: 1.5; 
        font-weight: 400; 
    }
    
    .principle-line {
        background: rgba(99, 102, 241, 0.1);
        border: 1px dashed rgba(99, 102, 241, 0.4);
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 0.88rem;
        color: #E0E7FF;
        margin-top: 8px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. HEADER & PERSUASION ACADEMY MODULE
# ==============================================================================
st.markdown('<span class="brand-badge">⚡ AI Copy & Pitch Growth Advisor</span>', unsafe_allow_html=True)
st.markdown('<div class="main-title">SiteGlow AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Diagnoses website copy and pitch text, rewrites hero sections into high-converting layouts, and teaches '
    'customer persuasion psychology — powered by Parallel Competitor Battles & Heatmap Labs.</div>',
    unsafe_allow_html=True
)

ACADEMY_LESSONS = [
    ("1. Outcome Over Features (Clarity First)", 
     "Visitors judge your offer in under 3 seconds. If your primary headline states what your product 'is' rather than what problem it solves, conversion drops sharply."),
    ("2. High-Intent Value Propositions", 
     "People buy outcomes, speed, and status. Frame supporting text around time saved, money gained, or pain eliminated rather than technical specifications."),
    ("3. Action-Reward CTAs", 
     "Generic buttons like 'Submit' or 'Learn More' create friction. Action buttons convert highest when they clearly state what the visitor receives ('Get My Free Audit')."),
]

with st.expander("🎓 CRO Academy — Persuasion Essentials & Rules", expanded=False):
    for title, body in ACADEMY_LESSONS:
        st.markdown(
            f'<div class="lesson-card"><div class="lesson-title">{title}</div>'
            f'<div class="lesson-body">{body}</div></div>',
            unsafe_allow_html=True
        )

# ==============================================================================
# 3. HELPER FUNCTIONS & SCRAPING ENGINE
# ==============================================================================
def esc(value):
    return html_lib.escape(str(value or ""), quote=True)

def clean_json_response(text):
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text

def is_url_pattern(text):
    text = (text or "").strip()
    if not text or '\n' in text or ' ' in text:
        return False
    if text.startswith("http://") or text.startswith("https://"):
        return True
    domain_pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?::\d+)?(?:/.*)?$'
    return bool(re.match(domain_pattern, text))

def normalize_url(text):
    text = text.strip()
    if not (text.startswith("http://") or text.startswith("https://")):
        return f"https://{text}"
    return text

def extract_website_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        meta_desc = ""
        meta_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        if meta_tag and meta_tag.get('content'):
            meta_desc = meta_tag['content'].strip()

        h1_list = [h.get_text().strip() for h in soup.find_all('h1') if h.get_text().strip()]
        h2_list = [h.get_text().strip() for h in soup.find_all('h2') if h.get_text().strip()]
        paragraphs = [p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()][:4]

        primary_h1 = h1_list[0] if h1_list else title
        primary_h2 = h2_list[0] if h2_list else meta_desc

        text_content = f"Page Title: {title}\nPrimary Headline (H1): {primary_h1}\nSubheadline (H2): {primary_h2}\nMeta Description: {meta_desc}\nSample Copy: {' '.join(paragraphs)}"[:1800]
        return {
            "text_content": text_content if len(text_content) > 25 else None,
            "h1": primary_h1 or title or "Original Headline",
            "h2": primary_h2 or meta_desc or "Original Subheadline",
            "body": meta_desc or (' '.join(paragraphs)) or "No description provided."
        }
    except Exception:
        return None

def process_input(raw_text):
    text = (raw_text or "").strip()
    if is_url_pattern(text):
        full_url = normalize_url(text)
        scraped_data = extract_website_content(full_url)
        if scraped_data is None or scraped_data["text_content"] is None:
            return None, True, None, f"Could not scrape URL `{full_url}`. Please ensure the domain is public or paste product text directly."
        return scraped_data["text_content"], True, scraped_data, None
    
    sentences = [s.strip() for s in re.split(r'[.\n]', text) if s.strip()]
    
    if len(sentences) <= 1:
        h1 = sentences[0][:120] if sentences else (text[:120] if text else "Original Headline")
        h2 = "Original Pitch / Value Proposition"
        body = "No additional body copy supplied."
    else:
        h1 = sentences[0][:120]
        h2 = sentences[1][:160]
        body = ' '.join(sentences[2:]) if len(sentences) > 2 else sentences[1]
    
    structured_fallback = {
        "h1": h1,
        "h2": h2,
        "body": body
    }
    return text, False, structured_fallback, None

# ==============================================================================
# 4. GEMINI API & PROMPT LOGIC
# ==============================================================================
@st.cache_data(ttl=3600)
def get_available_models_cached(api_key):
    genai.configure(api_key=api_key)
    try:
        all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        priority_list = [
            "models/gemini-2.5-pro",
            "models/gemini-2.5-flash",
            "models/gemini-2.0-flash",
            "models/gemini-1.5-pro",
            "models/gemini-1.5-flash"
        ]
        available = [m for m in priority_list if m in all_models] + [m for m in all_models if m not in priority_list]
        return available if available else ["models/gemini-1.5-flash"]
    except Exception:
        return ["models/gemini-1.5-flash"]

def build_prompt(processed_copy, is_url_source=False):
    source_label = "Live Website Scraped Data" if is_url_source else "Product Pitch Text"
    return f"""
    You are an elite Conversion Rate Optimization (CRO) expert and marketing strategist.
    Analyze this {source_label}:
    "{processed_copy}"

    INSTRUCTIONS:
    1. Evaluate 3 KEY AREAS of their offer:
       a) Main Title (Headline)
       b) Main Offer (Value Proposition)
       c) Next Step (Call to Action)
    2. If an area is already great, start the flaw text with "Optimal — " followed by praise.
    3. Produce 2 DISTINCT HIGH-CONVERTING HERO PREVIEW VARIANTS:
       - Option A: Outcome & Transformation Focused
       - Option B: Speed, Ease, or Direct Pain-Relief Focused

    Return ONLY valid JSON with this exact schema (no extra prose or markdown wrappers):
    {{
        "original_score": 74.0,
        "clarity_score": 70,
        "benefit_score": 75,
        "urgency_score": 50,
        "friction_score": 65,
        "headline_flaw": "Focuses on internal software mechanics rather than the user result.",
        "headline_lesson": "Headlines convert best when stating immediate outcomes.",
        "value_prop_flaw": "Optimal — Clear description of core target audience.",
        "value_prop_lesson": "Subheadlines should immediately reinforce the headline's main promise.",
        "cta_flaw": "Generic button text ('Submit') creates user hesitation.",
        "cta_lesson": "Action-oriented CTAs specifying immediate reward increase conversion.",
        "badge_text": "AI POWERED SOLUTION",
        "social_proof": "Loved by 10,000+ active users",
        "headline_a": "Eliminate Bottlenecks & Scale Team Output",
        "subheadline_a": "Unify team communication and project workflows into one intelligent dashboard.",
        "headline_b": "Stop Wasting Time on Scattered Tasks",
        "subheadline_b": "Get full visual control over team projects in under 5 minutes.",
        "cta_primary": "Get Started Free",
        "cta_secondary": "Watch Quick Demo"
    }}
    """

def run_gemini_analysis(processed_copy, is_url_source, available_models):
    prompt = build_prompt(processed_copy, is_url_source)
    for model_name in available_models:
        try:
            model = genai.GenerativeModel(
                model_name,
                generation_config={"response_mime_type": "application/json"}
            )
            response = model.generate_content(prompt)
            if response and response.text:
                clean_text = clean_json_response(response.text)
                data = json.loads(clean_text)
                return data, model_name
        except Exception:
            time.sleep(0.5)
            continue
    return None, None

def normalize_data(data):
    try:
        orig_score = round(float(data.get("original_score", 65.0)), 1)
    except Exception:
        orig_score = 65.0

    return {
        "orig_score": orig_score,
        "clarity": data.get("clarity_score", 60),
        "benefit": data.get("benefit_score", 50),
        "urgency": data.get("urgency_score", 40),
        "friction": data.get("friction_score", 70),
        "headline_flaw": data.get("headline_flaw", "Needs a stronger hook focused on direct customer results."),
        "headline_lesson": data.get("headline_lesson", "Headlines convert best when stating immediate outcomes."),
        "value_flaw": data.get("value_prop_flaw", "Could explain the primary benefit more clearly."),
        "value_lesson": data.get("value_prop_lesson", "Supporting copy should clarify the main value promise."),
        "cta_flaw": data.get("cta_flaw", "Button text needs higher urgency and a clearer reward."),
        "cta_lesson": data.get("cta_lesson", "Action-oriented CTAs specifying immediate value reduce decision hesitation."),
        "badge": data.get("badge_text", "AI POWERED SOLUTION"),
        "social_proof": data.get("social_proof", "Loved by thousands of active users"),
        "headline_a": data.get("headline_a", data.get("rewritten_headline", "Transform Your Results")),
        "subheadline_a": data.get("subheadline_a", data.get("rewritten_subheadline", "The simplest way to get better outcomes.")),
        "headline_b": data.get("headline_b", "Stop Wasting Time on Complex Tools"),
        "subheadline_b": data.get("subheadline_b", "Get professional-grade results in seconds."),
        "cta_primary": data.get("cta_primary", "Get Started Free"),
        "cta_secondary": data.get("cta_secondary", "Watch Quick Demo"),
    }

def analyze_single_site_task(raw_input, available_models):
    processed_text, is_url, structured_snap, error_msg = process_input(raw_input)
    if error_msg:
        return {"status": "error", "error": error_msg}

    raw_data, used_model = run_gemini_analysis(processed_text, is_url, available_models)

    if raw_data is None:
        return {"status": "error", "error": "Gemini API failed to return structured analysis. Please check your key or quotas."}

    norm_data = normalize_data(raw_data)
    norm_data["used_model"] = used_model
    return {
        "status": "success",
        "data": norm_data,
        "before": structured_snap,
        "is_url": is_url
    }

# ==============================================================================
# 5. UI COMPONENTS & PREVIEW TEMPLATES
# ==============================================================================
def get_status_badge(flaw_text):
    clean = str(flaw_text).strip().lower()
    if clean.startswith("none") or clean.startswith("optimal") or "strong" in clean or "excellent" in clean:
        return "<span style='color:#34D399; font-weight:800;'>[Optimal]</span>"
    return "<span style='color:#F87171; font-weight:800;'>[Needs Work]</span>"

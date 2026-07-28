import streamlit as st
import google.generativeai as genai
import json
import re
import html as html_lib
import requests
from bs4 import BeautifulSoup
import time
import concurrent.futures

# App Layout Configuration
st.set_page_config(page_title="SiteGlow AI — Conversion Engine", layout="wide")

# Modern Dark SaaS Styling
st.markdown("""
<style>
    .stApp { background-color: #090D16; color: #E2E8F0; }
    
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
    .main-title { font-size: 2.8rem; font-weight: 900; color: #FFFFFF; letter-spacing: -0.03em; margin-bottom: 6px; }
    .sub-title { font-size: 1.1rem; color: #94A3B8; margin-bottom: 28px; font-weight: 500; line-height: 1.5; }
    
    .stTextArea textarea {
        background-color: #111827 !important;
        border: 1px solid #1F2937 !important;
        color: #F9FAFB !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    .stTextArea textarea:focus { border-color: #6366F1 !important; box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important; }
    
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
    
    div[data-testid="stMetricValue"] { font-size: 2.2rem !important; font-weight: 900 !important; color: #818CF8 !important; }
    
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
    .lesson-title { color: #A5B4FC; font-weight: 800; font-size: 1rem; margin-bottom: 4px; }
    .lesson-body { color: #D1D5DB; font-size: 0.92rem; line-height: 1.5; font-weight: 400; }
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

# Header
st.markdown('<span class="brand-badge">⚡ AI CRO Tutor & Auto-Redesign Engine</span>', unsafe_allow_html=True)
st.markdown('<div class="main-title">SiteGlow AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Diagnoses website copy and pitch text, rewrites hero sections into high-converting layouts, and teaches '
    'conversion psychology — powered by Parallel Competitor Battles & Heatmap Labs.</div>',
    unsafe_allow_html=True
)

# CRO Academy Lessons
ACADEMY_LESSONS = [
    ("Clarity", "Visitors decide whether to stay within 3 seconds. If a headline describes a feature instead of the desired outcome, visitors leave."),
    ("Benefit Framing", "People buy transformation, not features: time saved, friction removed, revenue earned. Feature copy reads like a catalog; outcome copy converts."),
    ("Urgency & Scarcity", "Action drops without momentum. A generic 'Submit' button creates cognitive drag; a benefit-tied, action-oriented CTA drives high conversion."),
    ("Cognitive Friction", "Every extra step or ambiguous sentence increases drop-off. Minimizing mental resistance keeps users focused on the main value prop."),
    ("Visual Attention (F-Pattern)", "Visitors scan pages in predictable patterns, focusing on top headlines, badges, and primary CTAs before decaying rapidly."),
]

with st.expander("CRO Academy — Conversion Psychology Principles", expanded=False):
    st.caption("Learn the principles powering SiteGlow AI's scoring engine:")
    for title, body in ACADEMY_LESSONS:
        st.markdown(
            f'<div class="lesson-card"><div class="lesson-title">{title}</div>'
            f'<div class="lesson-body">{body}</div></div>',
            unsafe_allow_html=True
        )

# Helper Utilities
def esc(value):
    """HTML escaping helper function."""
    return html_lib.escape(str(value or ""), quote=True)

def clean_json_response(text):
    """Strips markdown formatting to prevent JSON decode errors."""
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
    except requests.exceptions.RequestException:
        return None

def process_input(raw_text):
    text = (raw_text or "").strip()
    if is_url_pattern(text):
        full_url = normalize_url(text)
        scraped_data = extract_website_content(full_url)
        if scraped_data is None or scraped_data["text_content"] is None:
            return None, True, None, f"Could not scrape URL `{full_url}`. Please ensure the domain is accessible or paste pitch text directly."
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

@st.cache_data(ttl=3600)
def get_available_models_cached(api_key):
    """Cache the models list to avoid redundant API hits per run."""
    genai.configure(api_key=api_key)
    try:
        all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        priority_list = [
            "models/gemini-3.1-pro",
            "models/gemini-2.5-pro",
            "models/gemini-2.5-flash",
        ]
        available = [m for m in priority_list if m in all_models] + [m for m in all_models if m not in priority_list]
        return available if available else ["models/gemini-1.5-flash"]
    except Exception:
        return ["models/gemini-1.5-flash"]

def get_execution_message(user_in, comp_in="", is_battle=False):
    u_is_url = is_url_pattern(user_in)
    if not is_battle:
        if u_is_url:
            clean_domain = user_in.strip().replace("https://", "").replace("http://", "").split('/')[0]
            return f"Live Scraping & Analyzing: {clean_domain}..."
        else:
            return "Analyzing Product Pitch Copy & Persuasion Logic..."
    else:
        c_is_url = is_url_pattern(comp_in)
        if u_is_url and c_is_url:
            return "Scraper Active: Live Analyzing Both Websites in Parallel..."
        elif u_is_url or c_is_url:
            return "Hybrid Engine: Scraping Live Domain & Evaluating Pitch Text..."
        else:
            return "Pitch Battle: Comparing Copywriting Psychology & Value Props..."

def build_prompt(processed_copy, is_url_source=False):
    source_label = "Live Website Scraped Data" if is_url_source else "Product Pitch Text"
    return f"""
    You are an elite, realistic Conversion Rate Optimization (CRO) Director.
    Analyze this {source_label}:
    "{processed_copy}"

    EVALUATION INSTRUCTIONS:
    1. Assess the text for true conversion potential based on Clarity, Urgency, Benefit Alignment, and Cognitive Friction.
    2. BE PRAGMATIC AND REALISTIC. Do not invent flaws if the copy is genuinely effective.
    3. If an element (Headline, Value Prop, CTA) has a significant, conversion-killing flaw, identify it clearly.
    4. IF THE ELEMENT IS ALREADY STRONG AND EFFECTIVE, start the flaw text exactly with: "Optimal — " followed by a brief explanation of why it works.
    5. For any actual flaw found, provide a transferable 1-sentence CRO psychological principle explaining *why* fixing it boosts conversion.
    6. Rewrite the messaging into an elite, high-converting Hero Block section (Badge, Headline, Subheadline, Primary CTA, Secondary CTA, Social Proof).

    Return ONLY valid JSON matching this exact schema (no markdown formatting):
    {{
        "original_score": 64.5,
        "clarity_score": 55,
        "urgency_score": 35,
        "benefit_score": 50,
        "friction_score": 65,
        "headline_flaw": "Focuses on process rather than the tangible user outcome.",
        "headline_lesson": "Headlines convert significantly higher when stating immediate transformation over feature details.",
        "value_prop_flaw": "Optimal — Communicates specific numerical value immediately.",
        "value_prop_lesson": "Quantified metrics build trust and reduce doubt faster than adjectives.",
        "cta_flaw": "Generic, high-friction button text with low incentive.",
        "cta_lesson": "Action-oriented CTAs specifying immediate value reduce decision hesitation.",
        "badge_text": "AUTOMATED WORKFLOW ENGINE",
        "social_proof": "Trusted by 10,000+ high-growth teams",
        "rewritten_headline": "Eliminate Bottlenecks & Scale Team Execution",
        "rewritten_subheadline": "Unify communication and project workflows into one fast, intelligent dashboard.",
        "cta_primary": "Start Free 14-Day Trial",
        "cta_secondary": "Watch 2-Min Demo"
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
        "urgency": data.get("urgency_score", 40),
        "benefit": data.get("benefit_score", 50),
        "friction": data.get("friction_score", 70),
        "headline_flaw": data.get("headline_flaw", "Focuses on building internal process rather than end user value."),
        "headline_lesson": data.get("headline_lesson", "Headlines convert better when stating outcomes over mechanism."),
        "value_flaw": data.get("value_prop_flaw", "Lists commodity feature lists without clear stakes."),
        "value_lesson": data.get("value_prop_lesson", "Quantified benefit metrics build trust faster."),
        "cta_flaw": data.get("cta_flaw", "Low-energy CTA button text with low urgency."),
        "cta_lesson": data.get("cta_lesson", "Specific action verbs outperform passive CTA copy."),
        "badge": data.get("badge_text", "AI WORKFLOW ENGINE"),
        "social_proof": data.get("social_proof", "Loved by 5,000+ founders"),
        "headline": data.get("rewritten_headline", "Eliminate Chaos & Scale Execution"),
        "subheadline": data.get("rewritten_subheadline", "Streamline collaboration with an intelligent workspace."),
        "cta_primary": data.get("cta_primary", "Get Started Free"),
        "cta_secondary": data.get("cta_secondary", "View Live Demo"),
    }

def analyze_single_site_task(raw_input, available_models):
    processed_text, is_url, structured_snap, error_msg = process_input(raw_input)
    if error_msg:
        return {"status": "error", "error": error_msg}

    raw_data, used_model = run_gemini_analysis(processed_text, is_url, available_models)

    if raw_data is None:
        return {"status": "error", "error": "Gemini API failed to return structured CRO analysis. Please check your key or rate limits."}

    norm_data = normalize_data(raw_data)
    norm_data["used_model"] = used_model
    return {
        "status": "success",
        "data": norm_data,
        "before": structured_snap,
        "is_url": is_url
    }

def get_status_badge(flaw_text):
    clean = str(flaw_text).strip().lower()
    if clean.startswith("none") or clean.startswith("optimal") or "strong" in clean or "excellent" in clean:
        return "<span style='color:#34D399; font-weight:800;'>[Optimal]</span>"
    return "<span style='color:#F87171; font-weight:800;'>[Flaw Detected]</span>"

def compute_winner(main, comp):
    main_score = main["orig_score"]
    comp_score = comp["orig_score"]

    winner = "yours" if main_score > comp_score else ("competitor" if comp_score > main_score else "tie")
    gap = round(abs(main_score - comp_score), 1)

    sub_metrics = [
        ("Message Clarity", main["clarity"], comp["clarity"], True),
        ("Benefit Alignment", main["benefit"], comp["benefit"], True),
        ("CTA Urgency", main["urgency"], comp["urgency"], True),
        ("Friction (lower is better)", main["friction"], comp["friction"], False),
    ]

    breakdown = []
    for label, m_val, c_val, higher_is_better in sub_metrics:
        side_winner = "yours" if (m_val > c_val if higher_is_better else m_val < c_val) else ("competitor" if (c_val > m_val if higher_is_better else c_val < m_val) else "tie")
        breakdown.append((label, m_val, c_val, side_winner, abs(m_val - c_val)))

    return winner, gap, breakdown

def render_hero_preview(fields, before_snapshot, variant_id):
    badge = esc(fields["badge"])
    headline = esc(fields["headline"])
    subheadline = esc(fields["subheadline"])
    cta_primary = esc(fields["cta_primary"])
    cta_secondary = esc(fields["cta_secondary"])
    social_proof = esc(fields["social_proof"])
    
    before_h1 = esc(before_snapshot.get("h1", "Original Headline"))
    before_h2 = esc(before_snapshot.get("h2", "Original Subheadline"))
    before_body = esc(before_snapshot.get("body", "Original Description"))

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="[https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800;900&display=swap](https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800;900&display=swap)" rel="stylesheet">
        <style>
            * {{ box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }}
            body {{ background-color: #090d16; color: #ffffff; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }}
            
            /* Modern Toolbar */
            .toolbar {{ display: flex; gap: 10px; margin-bottom: 24px; flex-wrap: wrap; justify-content: center; }}
            .toolbar-btn {{
                background: rgba(255,255,255,0.05); color: #9CA3AF; border: 1px solid rgba(255,255,255,0.1);
                padding: 10px 18px; border-radius: 10px; font-size: 13px; font-weight: 800; cursor: pointer; transition: all 0.2s;
            }}
            .toolbar-btn:hover {{ background: rgba(255,255,255,0.1); color: #fff; }}
            .toolbar-btn.active {{ background: linear-gradient(135deg, #4F46E5, #7C3AED); color: #ffffff; border-color: transparent; }}
            
            /* Container Frame */
            .preview-container {{ width: 100%; max-width: 900px; position: relative; }}
            
            /* AI Redesign View Styles */
            .ai-view {{
                background: rgba(17, 24, 39, 0.9); border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 24px; padding: 60px 40px; text-align: center; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                position: relative; overflow: hidden; display: block;
            }}
            .ai-badge {{
                display: inline-block; background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3);
                color: #A5B4FC; font-size: 12px; font-weight: 800; padding: 6px 16px; border-radius: 20px; 
                text-transform: uppercase; letter-spacing: 1px; margin-bottom: 24px;
            }}
            .ai-h1 {{ font-size: 42px; font-weight: 900; color: #fff; margin: 0 0 24px 0; line-height: 1.15; letter-spacing: -0.02em; }}
            .ai-h2 {{ font-size: 18px; color: #cbd5e1; margin: 0 auto 32px auto; max-width: 600px; line-height: 1.6; font-weight: 500; }}
            .ai-buttons {{ display: flex; gap: 16px; justify-content: center; margin-bottom: 24px; flex-wrap: wrap; }}
            .btn-primary {{
                background: linear-gradient(135deg, #4F46E5, #7C3AED); color: white; border: none;
                padding: 14px 32px; border-radius: 12px; font-size: 16px; font-weight: 800; cursor: pointer;
                box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4);
            }}
            .btn-secondary {{
                background: rgba(30, 41, 59, 0.8); color: #e2e8f0; border: 1px solid #334155;
                padding: 14px 32px; border-radius: 12px; font-size: 16px; font-weight: 800; cursor: pointer;
            }}
            .ai-proof {{ font-size: 13px; color: #94a3b8; font-weight: 700; }}
            
            /* Original View Styles */
            .orig-view {{
                background: #0f172a; border: 1px solid #1e293b; border-radius: 24px; padding: 60px 40px; text-align: left;
                display: none; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            }}
            .orig-badge {{
                display: inline-block; background: #1e293b; color: #cbd5e1; font-size: 12px; font-weight: 800;
                padding: 6px 14px; border-radius: 8px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 24px;
            }}
            .orig-h1 {{ font-size: 32px; font-weight: 800; color: #fff; margin: 0 0 16px 0; line-height: 1.3; }}
            .orig-h2 {{ font-size: 20px; font-weight: 600; color: #a5b4fc; margin: 0 0 24px 0; }}
            .orig-p {{ font-size: 16px; color: #94a3b8; margin: 0 0 32px 0; line-height: 1.6; max-width: 700px; }}
            .orig-btn {{ background: #334155; color: white; border: none; padding: 12px 24px; border-radius: 12px; font-size: 14px; font-weight: 700; cursor: pointer; }}
            
            /* Heatmap Overlay */
            #heatmap-{variant_id} {{ opacity: 0; pointer-events: none; transition: opacity 0.35s ease; position: absolute; inset: 0; z-index: 10; }}
            .heat-zone {{ position: absolute; border-radius: 20px; mix-blend-mode: screen; }}
            .heat-label {{
                position: absolute; font-size: 12px; font-weight: 800; letter-spacing: 0.04em;
                padding: 6px 12px; border-radius: 20px; background: rgba(0,0,0,0.8);
                white-space: nowrap; z-index: 11; border: 1px solid rgba(255,255,255,0.1);
            }}
            .dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }}
            
            @media (max-width: 600px) {{
                .ai-h1 {{ font-size: 32px; }}
                .ai-buttons {{ flex-direction: column; width: 100%; }}
                .btn-primary, .btn-secondary {{ width: 100%; }}
            }}
        </style>
    </head>
    <body>
        <div class="toolbar">
            <button id="btn-redesign-{variant_id}" class="toolbar-btn active" onclick="showView('{variant_id}','redesign')">AI Redesign</button>
            <button id="btn-original-{variant_id}" class="toolbar-btn" onclick="showView('{variant_id}','original')">Original Content</button>
            <button id="btn-heat-{variant_id}" class="toolbar-btn" onclick="toggleHeatmap('{variant_id}')">Attention Heatmap</button>
        </div>

        <div class="preview-container">
            <!-- AI REDESIGN -->
            <div id="redesign-{variant_id}" class="ai-view">
                <span class="ai-badge">{badge}</span>
                <h1 class="ai-h1">{headline}</h1>
                <h2 class="ai-h2">{subheadline}</h2>
                <div class="ai-buttons">
                    <button class="btn-primary">{cta_primary}</button>
                    <button class="btn-secondary">{cta_secondary}</button>
                </div>
                <div class="ai-proof">{social_proof}</div>

                <!-- Heatmap Overlay -->
                <div id="heatmap-{variant_id}">
                    <div class="heat-zone" style="top:15%; left:10%; width:80%; height:30%; background:radial-gradient(ellipse at center, rgba(239,68,68,0.7), rgba(239,68,68,0) 70%);"></div>
                    <span class="heat-label" style="top:20%; left:50%; transform:translateX(-50%); color:#FCA5A5;">
                        <span class="dot" style="background:#EF4444;"></span> 65% Headline Focus
                    </span>
                    <div class="heat-zone" style="top:60%; left:20%; width:60%; height:20%; background:radial-gradient(ellipse at center, rgba(250,204,21,0.6), rgba(250,204,21,0) 70%);"></div>
                    <span class="heat-label" style="top:68%; left:50%; transform:translateX(-50%); color:#FDE68A;">
                        <span class="dot" style="background:#FACC15;"></span> 25% CTA Focus
                    </span>
                </div>
            </div>

            <!-- ORIGINAL CONTENT -->
            <div id="original-{variant_id}" class="orig-view">
                <span class="orig-badge">Original Supplied Structure</span>
                <h1 class="orig-h1">{before_h1}</h1>
                <h2 class="orig-h2">{before_h2}</h2>
                <p class="orig-p">{before_body}</p>
                <button class="orig-btn">Learn More</button>
            </div>
        </div>

        <script>
            function showView(id, view) {{
                document.getElementById('redesign-' + id).style.display = (view === 'redesign') ? 'block' : 'none';
                document.getElementById('original-' + id).style.display = (view === 'original') ? 'block' : 'none';
                document.getElementById('btn-redesign-' + id).classList.toggle('active', view === 'redesign');
                document.getElementById('btn-original-' + id).classList.toggle('active', view === 'original');
            }}
            function toggleHeatmap(id) {{
                var hm = document.getElementById('heatmap-' + id);
                var isOn = hm.style.opacity === '1';
                hm.style.opacity = isOn ? '0' : '1';
                document.getElementById('btn-heat-' + id).classList.toggle('active', !isOn);
            }}
        </script>
    </body>
    </html>
    """

def render_single_scorecard(main):
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Conversion Health</div>', unsafe_allow_html=True)
        st.metric("Health Score", f"{main['orig_score']} / 100")
        st.caption(f"Engine Model: `{main['used_model']}`")
        st.write("---")
        st.write(f"**Message Clarity:** {main['clarity']}/100")
        st.progress(main["clarity"] / 100)
        st.write(f"**Value/Benefit Focus:** {main['benefit']}/100")
        st.progress(main["benefit"] / 100)
        st.write(f"**CTA Urgency:** {main['urgency']}/100")
        st.progress(main["urgency"] / 100)
        st.write(f"**Friction Level:** {main['friction']}/100")
        st.progress(main["friction"] / 100)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Conversion Diagnosis & Lessons</div>', unsafe_allow_html=True)
        st.markdown(f"#### {get_status_badge(main['headline_flaw'])} Headline Structure", unsafe_allow_html=True)
        st.write(main["headline_flaw"])
        st.markdown(f'<div class="principle-line"><b>Principle:</b> {esc(main["headline_lesson"])}</div>', unsafe_allow_html=True)
        st.write("---")
        st.markdown(f"#### {get_status_badge(main['value_flaw'])} Value Proposition", unsafe_allow_html=True)
        st.write(main["value_flaw"])
        st.markdown(f'<div class="principle-line"><b>Principle:</b> {esc(main["value_lesson"])}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def render_battle_scorecard(main, comp):
    winner, gap, breakdown = compute_winner(main, comp)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="site-label-blue">YOUR ITEM</span>', unsafe_allow_html=True)
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.metric("Score", f"{main['orig_score']} / 100")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<span class="site-label-red">COMPETITOR</span>', unsafe_allow_html=True)
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.metric("Score", f"{comp['orig_score']} / 100")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Competitor Battle Outcome</div>', unsafe_allow_html=True)
    if winner == "yours":
        st.markdown(f'<span class="winner-badge">Your site/pitch wins by {gap} points</span>', unsafe_allow_html=True)
    elif winner == "competitor":
        st.markdown(f'<span class="loser-badge">Competitor leads by {gap} points</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="brand-badge">Dead heat — scores are tied</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Engine Setup")
    raw_api_key = st.text_input("Enter Gemini API Key:", type="password")
    api_key = raw_api_key.strip() if raw_api_key else ""
    st.markdown("[Get a free key from Google AI Studio](https://aistudio.google.com/)")

battle_mode = st.toggle("Enable Competitor CRO Battle Mode", value=False)

if battle_mode:
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        user_input = st.text_area("Your website domain OR pitch copy:", height=140, key="user_input_battle", placeholder="e.g. basecamp.com or 'We build AI software that automates invoice creation...'")
    with col_in2:
        competitor_input = st.text_area("Competitor website domain OR pitch copy:", height=140, key="competitor_input_battle", placeholder="e.g. ghost.org or competitor product pitch")
else:
    user_input = st.text_area("Paste product pitch text OR enter website domain (e.g. basecamp.com, ghost.org, https://...):", height=120, key="user_input_single")
    competitor_input = ""

analyze_button = st.button("Analyze & Auto-Redesign", type="primary")

# Execution Handler
if analyze_button:
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    elif battle_mode and (not user_input.strip() or not competitor_input.strip()):
        st.warning("Please fill in both input fields for Battle Mode.")
    elif not battle_mode and not user_input.strip():
        st.warning("Please enter pitch copy or a domain URL.")
    else:
        exec_message = get_execution_message(user_input, competitor_input, battle_mode)
        with st.spinner(exec_message):
            genai.configure(api_key=api_key)
            available_models = get_available_models_cached(api_key)

            if battle_mode:
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    future_main = executor.submit(analyze_single_site_task, user_input, available_models)
                    future_comp = executor.submit(analyze_single_site_task, competitor_input, available_models)
                    
                    res_main = future_main.result()
                    res_comp = future_comp.result()

                if res_main["status"] == "error":
                    st.session_state['has_data'] = False
                    st.error(f"Your Site/Pitch Error: {res_main['error']}")
                elif res_comp["status"] == "error":
                    st.session_state['has_data'] = False
                    st.error(f"Competitor Error: {res_comp['error']}")
                else:
                    st.session_state['has_data'] = True
                    st.session_state['main'] = res_main["data"]
                    st.session_state['before_main'] = res_main["before"]
                    st.session_state['comp'] = res_comp["data"]
                    st.session_state['before_comp'] = res_comp["before"]
                    st.session_state['battle_mode'] = True

            else:
                res_main = analyze_single_site_task(user_input, available_models)
                if res_main["status"] == "error":
                    st.session_state['has_data'] = False
                    st.error(f"Error: {res_main['error']}")
                else:
                    st.session_state['has_data'] = True
                    st.session_state['main'] = res_main["data"]
                    st.session_state['before_main'] = res_main["before"]
                    st.session_state['comp'] = None
                    st.session_state['before_comp'] = None
                    st.session_state['battle_mode'] = False

# Render Output UI
if st.session_state.get('has_data', False):
    main = st.session_state['main']
    before_main = st.session_state['before_main']
    comp = st.session_state['comp']
    before_comp = st.session_state['before_comp']
    is_battle = st.session_state['battle_mode']

    tab1, tab2, tab3 = st.tabs(["CRO Scorecard", "Live Hero Redesign", "Export Code"])

    with tab1:
        if is_battle and comp:
            render_battle_scorecard(main, comp)
        else:
            render_single_scorecard(main)

    with tab2:
        if is_battle and comp:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<span class="site-label-blue">YOUR SITE / PITCH</span>', unsafe_allow_html=True)
                st.components.v1.html(render_hero_preview(main, before_main, "main"), height=680, scrolling=True)
            with c2:
                st.markdown('<span class="site-label-red">COMPETITOR</span>', unsafe_allow_html=True)
                st.components.v1.html(render_hero_preview(comp, before_comp, "comp"), height=680, scrolling=True)
        else:
            st.components.v1.html(render_hero_preview(main, before_main, "main"), height=680, scrolling=True)

    with tab3:
        st.subheader("Ready-to-Use HTML")
        if is_battle and comp:
            sub1, sub2 = st.tabs(["Your Item HTML", "Competitor Item HTML"])
            with sub1:
                html_main = render_hero_preview(main, before_main, "main")
                st.caption("Hero section HTML code for **Your Item**:")
                st.code(html_main, language="html")
                st.download_button("Download Your Item HTML", data=html_main, file_name="your_hero_redesign.html", mime="text/html")
            with sub2:
                html_comp = render_hero_preview(comp, before_comp, "comp")
                st.caption("Hero section HTML code for **Competitor**:")
                st.code(html_comp, language="html")
                st.download_button("Download Competitor HTML", data=html_comp, file_name="competitor_hero.html", mime="text/html")
        else:
            html_main = render_hero_preview(main, before_main, "main")
            st.code(html_main, language="html")
            st.download_button("Download Hero HTML", data=html_main, file_name="hero_redesign.html", mime="text/html")

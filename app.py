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
st.set_page_config(page_title="SiteGlow AI — Conversion & Design Engine", page_icon="⚡", layout="wide")

# Modern SaaS Styling with High Contrast & Bold Typography
st.markdown("""
<style>
    .stApp { background-color: #090D16; color: #E2E8F0; }
    
    /* Header Typography */
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
    
    /* Input Styling */
    .stTextArea textarea {
        background-color: #111827 !important;
        border: 1px solid #1F2937 !important;
        color: #F9FAFB !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    .stTextArea textarea:focus { border-color: #6366F1 !important; box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important; }
    
    /* Button Styling */
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
    
    /* Cards & Containers */
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

# Header Section
st.markdown('<span class="brand-badge">⚡ AI CRO Tutor & Auto-Redesign Engine</span>', unsafe_allow_html=True)
st.markdown('<div class="main-title">SiteGlow AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Diagnoses website copy, rewrites heroes into high-converting layouts, and teaches '
    'conversion psychology — powered by Parallel Competitor Battles & Heatmap Labs.</div>',
    unsafe_allow_html=True
)

# CRO Academy
ACADEMY_LESSONS = [
    ("🔍 Clarity", "Visitors decide whether to keep reading within seconds. If a headline describes a feature instead of the outcome, visitors leave rather than translate it."),
    ("🎁 Benefit Framing", "People buy outcomes: time saved, stress removed, revenue earned. Copy listing features reads like a catalog; copy naming transformation drives action."),
    ("⏳ Urgency & Scarcity", "People act faster when moments feel timely. A generic 'Submit' button asks for effort; a specific, value-bound CTA gives a reason to click now."),
    ("🧠 Cognitive Friction", "Every extra decision or vague step adds mental load. Lower friction makes the primary next step obvious at a single glance."),
    ("👁️ Visual Attention (F-Pattern)", "Visitors scan pages in predictable patterns, spending most attention on headlines and hero elements before decaying sharply."),
]

with st.expander("🎓 CRO Academy — Conversion Psychology Principles", expanded=False):
    st.caption("Learn the principles powering SiteGlow AI's scoring engine:")
    for title, body in ACADEMY_LESSONS:
        st.markdown(
            f'<div class="lesson-card"><div class="lesson-title">{title}</div>'
            f'<div class="lesson-body">{body}</div></div>',
            unsafe_allow_html=True
        )

# URL Parser & Scraper Logic
def is_url_pattern(text):
    text = text.strip()
    if ' ' in text or '\n' in text:
        return False
    if text.startswith("http://") or text.startswith("https://"):
        return True
    domain_pattern = r'^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/.*)?$'
    return bool(re.match(domain_pattern, text))

def normalize_url(text):
    text = text.strip()
    if not (text.startswith("http://") or text.startswith("https://")):
        return f"https://{text}"
    return text

def extract_website_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=6)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        meta_desc = ""
        meta_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        if meta_tag and meta_tag.get('content'):
            meta_desc = meta_tag['content'].strip()

        headings = [h.get_text().strip() for h in soup.find_all(['h1', 'h2']) if h.get_text().strip()]
        paragraphs = [p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()][:3]

        text_content = f"Page Title: {title}\nMeta Description: {meta_desc}\nHeadings: {' | '.join(headings[:4])}\nSample Copy: {' '.join(paragraphs)}"[:1500]
        return text_content if len(text_content) > 30 else None
    except Exception:
        return None

def process_input(raw_text):
    """Returns (processed_text, is_url, error_message)"""
    text = (raw_text or "").strip()
    if is_url_pattern(text):
        full_url = normalize_url(text)
        scraped = extract_website_content(full_url)
        if scraped is None:
            return None, True, f"Could not reach or scrape the URL `{full_url}`. Please verify the domain is reachable or paste product pitch text directly."
        return scraped, True, None
    return text, False, None

def build_before_snapshot(raw_input, processed_copy, is_url):
    if is_url:
        title_match = re.search(r'Page Title:\s*(.*)', processed_copy or "")
        meta_match = re.search(r'Meta Description:\s*(.*)', processed_copy or "")
        headline = title_match.group(1).strip() if title_match and title_match.group(1).strip() else "Original Headline"
        body = meta_match.group(1).strip() if meta_match and meta_match.group(1).strip() else (processed_copy[:220] if processed_copy else "")
    else:
        sentences = [s.strip() for s in re.split(r'[.\n]', raw_input) if s.strip()]
        headline = sentences[0][:120] if sentences else (raw_input[:120] if raw_input else "Original Headline")
        body = raw_input[:280] if raw_input else "No original copy supplied."

    return {"headline": headline or "Original Headline", "body": body or "No original copy supplied."}

def esc(value):
    return html_lib.escape(str(value), quote=True)

# Gemini Model Helper
def get_available_models():
    try:
        all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        priority_list = [
            "models/gemini-2.5-flash",
            "models/gemini-2.0-flash",
            "models/gemini-1.5-flash",
            "models/gemini-1.5-pro"
        ]
        available = [m for m in priority_list if m in all_models] + [m for m in all_models if m not in priority_list]
        return available if available else ["models/gemini-1.5-flash"]
    except Exception:
        return ["models/gemini-1.5-flash"]

def build_prompt(processed_copy):
    return f"""
    You are a world-class CRO strategist and SaaS visual designer.
    Analyze this business content: "{processed_copy}"

    EVALUATION RULES:
    1. Score from 15.0 to 99.0 based on persuasiveness.
    2. If an element is exceptional, start flaw text with "None — ".
    3. Rewrite messaging into a high-converting Hero block section.
    4. Provide rating scores (0-100) for Clarity, Urgency, Benefit Alignment, Friction.
    5. Provide a transferable 1-sentence CRO psychological lesson for each flaw.

    Return JSON matching this schema:
    {{
        "original_score": 42.5,
        "clarity_score": 50,
        "urgency_score": 30,
        "benefit_score": 40,
        "friction_score": 80,
        "headline_flaw": "Focuses on internal features.",
        "headline_lesson": "Headlines convert better when stating user outcomes.",
        "value_prop_flaw": "Lacks specific outcome metrics.",
        "value_prop_lesson": "Quantified outcomes build trust.",
        "cta_flaw": "Generic low-urgency button.",
        "cta_lesson": "Action-oriented CTAs increase conversions.",
        "badge_text": "AUTOMATED WORKFLOWS",
        "social_proof": "⚡ Trusted by 10,000+ teams",
        "rewritten_headline": "Bring Your Team into Alignment",
        "rewritten_subheadline": "Unify execution and communication in one fast dashboard.",
        "cta_primary": "Start Free Trial →",
        "cta_secondary": "Watch Demo"
    }}
    """

def run_gemini_analysis(processed_copy, available_models):
    prompt = build_prompt(processed_copy)
    for model_name in available_models:
        try:
            model = genai.GenerativeModel(
                model_name,
                generation_config={"response_mime_type": "application/json"}
            )
            response = model.generate_content(prompt)
            if response and response.text:
                data = json.loads(response.text)
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
        "headline_flaw": data.get("headline_flaw", "Focuses on internal building process rather than external results."),
        "headline_lesson": data.get("headline_lesson", "Headlines convert better when they state outcomes."),
        "value_flaw": data.get("value_prop_flaw", "Lists commodity features without emotional stakes."),
        "value_lesson": data.get("value_prop_lesson", "Quantified outcomes are more persuasive."),
        "cta_flaw": data.get("cta_flaw", "Low-energy CTA with minimal incentive."),
        "cta_lesson": data.get("cta_lesson", "Specific action verbs outperform passive buttons."),
        "badge": data.get("badge_text", "AI WORKFLOW ENGINE"),
        "social_proof": data.get("social_proof", "⚡ Loved by 5,000+ founders"),
        "headline": data.get("rewritten_headline", "Eliminate Chaos & Scale Execution"),
        "subheadline": data.get("rewritten_subheadline", "Streamline collaboration with an intelligent workspace."),
        "cta_primary": data.get("cta_primary", "Get Started Free →"),
        "cta_secondary": data.get("cta_secondary", "View Live Demo"),
    }

def analyze_single_site_task(raw_input, available_models):
    processed_text, is_url, error_msg = process_input(raw_input)
    if error_msg:
        return {"status": "error", "error": error_msg}

    before_snap = build_before_snapshot(raw_input, processed_text, is_url)
    raw_data, used_model = run_gemini_analysis(processed_text, available_models)

    if raw_data is None:
        return {"status": "error", "error": "Gemini API failed to generate analysis. Please verify your API key."}

    norm_data = normalize_data(raw_data)
    norm_data["used_model"] = used_model
    return {
        "status": "success",
        "data": norm_data,
        "before": before_snap,
        "is_url": is_url
    }

def get_status_badge(flaw_text):
    clean = flaw_text.strip().lower()
    if clean.startswith("none") or "strong" in clean or "excellent" in clean:
        return "✅ <span style='color:#34D399; font-weight:800;'>Optimal</span>"
    return "❌ <span style='color:#F87171; font-weight:800;'>Flaw Detected</span>"

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

    biggest = max(breakdown, key=lambda row: row[4]) if breakdown else None
    return winner, gap, breakdown, biggest

def render_hero_preview(fields, before_snapshot, variant_id):
    badge = esc(fields["badge"])
    headline = esc(fields["headline"])
    subheadline = esc(fields["subheadline"])
    cta_primary = esc(fields["cta_primary"])
    cta_secondary = esc(fields["cta_secondary"])
    social_proof = esc(fields["social_proof"])
    before_headline = esc(before_snapshot["headline"])
    before_body = esc(before_snapshot["body"])

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800;900&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Plus Jakarta Sans', sans-serif; background-color: #090d16; color: #ffffff; margin: 0; padding: 20px; }}
            .glass-card {{ background: rgba(17, 24, 39, 0.9); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }}
            .toolbar-btn {{ transition: all 0.15s ease; cursor: pointer; border: 1px solid rgba(255,255,255,0.1); }}
            .toolbar-btn.active {{ background: linear-gradient(135deg, #4F46E5, #7C3AED); color: #ffffff; border-color: transparent; }}
            .toolbar-btn:not(.active) {{ background: rgba(255,255,255,0.05); color: #9CA3AF; }}
            #original-{variant_id} {{ display: none; }}
            #heatmap-{variant_id} {{ opacity: 0; pointer-events: none; transition: opacity 0.35s ease; }}
            .heat-zone {{ position: absolute; border-radius: 18px; mix-blend-mode: screen; }}
            .heat-label {{
                position: absolute; font-size: 11px; font-weight: 800; letter-spacing: 0.04em;
                padding: 4px 10px; border-radius: 999px; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px);
                white-space: nowrap;
            }}
        </style>
    </head>
    <body>
        <div class="max-w-4xl mx-auto mb-4 flex flex-wrap items-center justify-center gap-2">
            <button id="btn-redesign-{variant_id}" class="toolbar-btn active text-xs font-extrabold px-4 py-2 rounded-lg" onclick="showView('{variant_id}','redesign')">✨ AI Redesign</button>
            <button id="btn-original-{variant_id}" class="toolbar-btn text-xs font-extrabold px-4 py-2 rounded-lg" onclick="showView('{variant_id}','original')">📝 Original</button>
            <button id="btn-heat-{variant_id}" class="toolbar-btn text-xs font-extrabold px-4 py-2 rounded-lg" onclick="toggleHeatmap('{variant_id}')">🔥 Attention Heatmap</button>
        </div>

        <div class="relative max-w-4xl mx-auto">
            <div id="redesign-{variant_id}" class="relative glass-card rounded-3xl p-8 md:p-12 shadow-2xl overflow-hidden">
                <div class="relative z-10 text-center">
                    <span class="inline-flex items-center gap-2 bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 text-xs font-extrabold px-4 py-1.5 rounded-full mb-6 uppercase tracking-wider">
                        ✨ {badge}
                    </span>
                    <h1 class="text-3xl md:text-5xl font-black tracking-tight text-white mb-6 leading-tight">{headline}</h1>
                    <p class="text-slate-300 text-base md:text-lg mb-8 max-w-2xl mx-auto leading-relaxed font-medium">{subheadline}</p>
                    <div class="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
                        <button class="w-full sm:w-auto bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-extrabold text-base px-8 py-3.5 rounded-xl shadow-lg">{cta_primary}</button>
                        <button class="w-full sm:w-auto bg-slate-800/90 text-slate-200 font-extrabold text-base px-7 py-3.5 rounded-xl border border-slate-700">{cta_secondary}</button>
                    </div>
                    <p class="text-xs text-slate-400 font-bold">{social_proof}</p>
                </div>

                <div id="heatmap-{variant_id}" class="absolute inset-0 z-20">
                    <div class="heat-zone" style="top:12%; left:10%; width:80%; height:26%; background:radial-gradient(ellipse at center, rgba(239,68,68,0.6), rgba(239,68,68,0) 70%);"></div>
                    <span class="heat-label" style="top:14%; left:50%; transform:translateX(-50%); color:#FCA5A5;">🔴 65% Headline Focus</span>
                    <div class="heat-zone" style="top:55%; left:25%; width:50%; height:20%; background:radial-gradient(ellipse at center, rgba(250,204,21,0.55), rgba(250,204,21,0) 70%);"></div>
                    <span class="heat-label" style="top:62%; left:50%; transform:translateX(-50%); color:#FDE68A;">🟡 25% CTA Focus</span>
                </div>
            </div>

            <div id="original-{variant_id}" class="relative bg-white rounded-2xl p-8 md:p-12 shadow-2xl text-center" style="font-family: Arial, sans-serif;">
                <span class="inline-block bg-gray-100 text-gray-600 text-xs font-bold px-3 py-1 rounded mb-4 uppercase">Before — Original Input</span>
                <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-4">{before_headline}</h1>
                <p class="text-gray-600 text-sm md:text-base mb-6 max-w-2xl mx-auto">{before_body}</p>
                <button class="bg-gray-800 text-white text-sm font-bold px-6 py-2.5 rounded">Submit</button>
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

# Render Scorecard Functions
def render_single_scorecard(main):
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"> Conversion Health</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="card-title">🔍 Conversion Diagnosis & Lessons</div>', unsafe_allow_html=True)
        st.markdown(f"#### {get_status_badge(main['headline_flaw'])} Headline Structure", unsafe_allow_html=True)
        st.write(main["headline_flaw"])
        st.markdown(f'<div class="principle-line">🎓 <b>Principle:</b> {esc(main["headline_lesson"])}</div>', unsafe_allow_html=True)
        st.write("---")
        st.markdown(f"#### {get_status_badge(main['value_flaw'])} Value Proposition", unsafe_allow_html=True)
        st.write(main["value_flaw"])
        st.markdown(f'<div class="principle-line">🎓 <b>Principle:</b> {esc(main["value_lesson"])}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def render_battle_scorecard(main, comp):
    winner, gap, breakdown, biggest = compute_winner(main, comp)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="site-label-blue">🟦 YOUR SITE</span>', unsafe_allow_html=True)
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.metric("Score", f"{main['orig_score']} / 100")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<span class="site-label-red">🟥 COMPETITOR</span>', unsafe_allow_html=True)
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.metric("Score", f"{comp['orig_score']} / 100")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🏆 Competitor Battle Outcome</div>', unsafe_allow_html=True)
    if winner == "yours":
        st.markdown(f'<span class="winner-badge">🏆 Your site wins by {gap} points</span>', unsafe_allow_html=True)
    elif winner == "competitor":
        st.markdown(f'<span class="loser-badge">⚠️ Competitor leads by {gap} points</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="brand-badge">🤝 Dead heat — scores are tied</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar Setup
with st.sidebar:
    st.header("⚙️ Engine Setup")
    raw_api_key = st.text_input("Enter Gemini API Key:", type="password")
    api_key = raw_api_key.strip() if raw_api_key else ""
    st.markdown("[Get a free key from Google AI Studio](https://aistudio.google.com/)")

# Input Interface
battle_mode = st.toggle("🥊 Enable Competitor CRO Battle Mode", value=False)

if battle_mode:
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        user_input = st.text_area("🟦 Your website URL or pitch text:", height=140, key="user_input_battle", placeholder="e.g. basecamp.com or product pitch text")
    with col_in2:
        competitor_input = st.text_area("🟥 Competitor website URL or pitch text:", height=140, key="competitor_input_battle", placeholder="e.g. ghost.org or competitor pitch text")
else:
    user_input = st.text_area("Paste product pitch OR enter website domain (e.g. basecamp.com, ghost.org):", height=120, key="user_input_single")
    competitor_input = ""

analyze_button = st.button("🚀 Analyze & Auto-Redesign Live", type="primary")

# Execute Parallel Analysis & Save in Session State
if analyze_button:
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    elif battle_mode and (not user_input.strip() or not competitor_input.strip()):
        st.warning("Please fill in both input fields for Battle Mode.")
    elif not battle_mode and not user_input.strip():
        st.warning("Please enter text or a URL.")
    else:
        with st.spinner("Executing parallel web scrapers and Gemini CRO analysis..."):
            genai.configure(api_key=api_key)
            available_models = get_available_models()

            if battle_mode:
                # Parallel execution for Battle Mode
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    future_main = executor.submit(analyze_single_site_task, user_input, available_models)
                    future_comp = executor.submit(analyze_single_site_task, competitor_input, available_models)
                    
                    res_main = future_main.result()
                    res_comp = future_comp.result()

                if res_main["status"] == "error":
                    st.error(f"❌ Your Site Error: {res_main['error']}")
                elif res_comp["status"] == "error":
                    st.error(f"❌ Competitor Site Error: {res_comp['error']}")
                else:
                    st.session_state['has_data'] = True
                    st.session_state['main'] = res_main["data"]
                    st.session_state['before_main'] = res_main["before"]
                    st.session_state['comp'] = res_comp["data"]
                    st.session_state['before_comp'] = res_comp["before"]
                    st.session_state['battle_mode'] = True

            else:
                # Single site execution
                res_main = analyze_single_site_task(user_input, available_models)
                if res_main["status"] == "error":
                    st.error(f"❌ Error: {res_main['error']}")
                else:
                    st.session_state['has_data'] = True
                    st.session_state['main'] = res_main["data"]
                    st.session_state['before_main'] = res_main["before"]
                    st.session_state['comp'] = None
                    st.session_state['before_comp'] = None
                    st.session_state['battle_mode'] = False

# Render Results from Session State
if st.session_state.get('has_data', False):
    main = st.session_state['main']
    before_main = st.session_state['before_main']
    comp = st.session_state['comp']
    before_comp = st.session_state['before_comp']
    is_battle = st.session_state['battle_mode']

    tab1, tab2, tab3 = st.tabs(["📊 CRO Scorecard", "✨ Live Hero Redesign", "💻 Export Code"])

    with tab1:
        if is_battle and comp:
            render_battle_scorecard(main, comp)
        else:
            render_single_scorecard(main)

    with tab2:
        if is_battle and comp:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<span class="site-label-blue">🟦 YOUR SITE</span>', unsafe_allow_html=True)
                st.components.v1.html(render_hero_preview(main, before_main, "main"), height=680, scrolling=True)
            with c2:
                st.markdown('<span class="site-label-red">🟥 COMPETITOR</span>', unsafe_allow_html=True)
                st.components.v1.html(render_hero_preview(comp, before_comp, "comp"), height=680, scrolling=True)
        else:
            st.components.v1.html(render_hero_preview(main, before_main, "main"), height=680, scrolling=True)

    with tab3:
        st.subheader("💻 Ready-to-Use Tailwind HTML")
        if is_battle and comp:
            sub1, sub2 = st.tabs(["🟦 Your Site HTML", "🟥 Competitor Site HTML"])
            with sub1:
                html_main = render_hero_preview(main, before_main, "main")
                st.caption("Hero section HTML code for **Your Site**:")
                st.code(html_main, language="html")
                st.download_button("📥 Download Your Site HTML", data=html_main, file_name="your_site_hero.html", mime="text/html")
            with sub2:
                html_comp = render_hero_preview(comp, before_comp, "comp")
                st.caption("Hero section HTML code for **Competitor Site**:")
                st.code(html_comp, language="html")
                st.download_button("📥 Download Competitor HTML", data=html_comp, file_name="competitor_hero.html", mime="text/html")
        else:
            html_main = render_hero_preview(main, before_main, "main")
            st.code(html_main, language="html")
            st.download_button("📥 Download Hero HTML", data=html_main, file_name="hero_redesign.html", mime="text/html")

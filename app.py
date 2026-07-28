import streamlit as st
import google.generativeai as genai
import json
import re
import html as html_lib
import requests
from bs4 import BeautifulSoup
import time

# App Layout Configuration
st.set_page_config(page_title="SiteGlow AI — Conversion & Design Engine", page_icon="⚡", layout="wide")

# Modern SaaS Styling with Custom CSS
st.markdown("""
<style>
    .stApp { background-color: #0B0F17; color: #E2E8F0; }
    
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
    
    .winner-badge {
        display: inline-block;
        background: linear-gradient(135deg, #10B981, #34D399);
        color: #052e1f;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.95rem;
        font-weight: 800;
    }
    .loser-badge {
        display: inline-block;
        background: rgba(248, 113, 113, 0.12);
        border: 1px solid rgba(248, 113, 113, 0.3);
        color: #F87171;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.95rem;
        font-weight: 800;
    }
    .site-label-blue {
        display: inline-block;
        background: rgba(59, 130, 246, 0.12);
        border: 1px solid rgba(59, 130, 246, 0.3);
        color: #60A5FA;
        padding: 3px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .site-label-red {
        display: inline-block;
        background: rgba(248, 113, 113, 0.12);
        border: 1px solid rgba(248, 113, 113, 0.3);
        color: #F87171;
        padding: 3px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .lesson-card {
        background: #131927;
        border: 1px solid #1E293B;
        border-left: 3px solid #6366F1;
        border-radius: 10px;
        padding: 16px 18px;
        margin-bottom: 12px;
    }
    .lesson-title { color: #A5B4FC; font-weight: 800; font-size: 0.95rem; margin-bottom: 4px; }
    .lesson-body { color: #CBD5E1; font-size: 0.88rem; line-height: 1.5; }
    .principle-line {
        background: rgba(99, 102, 241, 0.08);
        border: 1px dashed rgba(99, 102, 241, 0.35);
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 0.85rem;
        color: #C7D2FE;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown('<span class="brand-badge">⚡ AI CRO Tutor & Auto-Redesign Engine</span>', unsafe_allow_html=True)
st.markdown('<div class="main-title">SiteGlow AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Diagnoses real websites, rewrites them into high-converting heroes, and teaches '
    'the conversion psychology behind every fix — with Competitor Battle Mode & a live Attention-Heatmap Lab.</div>',
    unsafe_allow_html=True
)

# CRO Academy
ACADEMY_LESSONS = [
    ("🔍 Clarity", "Visitors decide whether to keep reading within seconds. If a headline describes a "
     "feature instead of the outcome a person gets, the brain has to do extra translation work — and most "
     "people simply leave instead of doing it."),
    ("🎁 Benefit Framing", "People don't buy tools, they buy outcomes: time saved, stress removed, money "
     "earned. Copy that lists specs reads as a catalog; copy that names the transformation reads as a reason "
     "to act."),
    ("⏳ Urgency & Scarcity", "Decision-making research shows people act faster when a moment feels limited or timely. "
     "A generic 'Submit' button asks for effort with nothing in return; a specific, time-bound CTA gives a reason to click now."),
    ("🧠 Cognitive Friction", "Every extra decision, unclear label, or vague next step adds mental load. Lower "
     "friction doesn't mean fewer words — it means the next step is obvious at a glance."),
    ("👁️ Visual Attention (F-Pattern)", "Eye-tracking studies from researchers like Nielsen Norman Group have "
     "repeatedly found that visitors scan pages in predictable patterns, spending most of their attention on "
     "the headline and hero area before decaying sharply."),
]

with st.expander("🎓 CRO Academy — The Psychology Powering This Tool", expanded=False):
    st.caption("SiteGlow AI isn't just a scoring tool — it's built to teach you *why* each principle moves the needle.")
    for title, body in ACADEMY_LESSONS:
        st.markdown(
            f'<div class="lesson-card"><div class="lesson-title">{title}</div>'
            f'<div class="lesson-body">{body}</div></div>',
            unsafe_allow_html=True
        )

# Helper Functions
def extract_website_content(url):
    """Scrapes content from URL cleanly, returning None if scrape fails."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=7)
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
        return text_content if len(text_content) > 50 else None
    except Exception:
        return None

def process_input(raw_text):
    """Returns (processed_copy, is_url, scrape_failed)"""
    text = (raw_text or "").strip()
    if text.startswith("http://") or text.startswith("https://"):
        st.info(f"🌐 Fetching live website content from `{text}`...")
        scraped = extract_website_content(text)
        if scraped is None:
            return text, True, True  # Fallback to URL as text string, flag failure
        return scraped, True, False
    return text, False, False

def build_before_snapshot(raw_input, processed_copy, is_url):
    if is_url:
        title_match = re.search(r'Page Title:\s*(.*)', processed_copy)
        meta_match = re.search(r'Meta Description:\s*(.*)', processed_copy)
        headline = title_match.group(1).strip() if title_match and title_match.group(1).strip() else "Your Original Headline"
        body = meta_match.group(1).strip() if meta_match and meta_match.group(1).strip() else processed_copy[:220]
    else:
        sentences = [s.strip() for s in re.split(r'[.\n]', raw_input) if s.strip()]
        headline = sentences[0][:120] if sentences else (raw_input[:120] if raw_input else "Your Original Headline")
        body = raw_input[:280] if raw_input else "No original copy supplied."

    return {"headline": headline or "Your Original Headline", "body": body or "No original copy supplied."}

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
            # Force Native JSON output from Gemini
            model = genai.GenerativeModel(
                model_name,
                generation_config={"response_mime_type": "application/json"}
            )
            response = model.generate_content(prompt)
            if response and response.text:
                data = json.loads(response.text)
                return data, model_name
        except Exception:
            time.sleep(1) # Brief pause on retry
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

def get_status_badge(flaw_text):
    clean = flaw_text.strip().lower()
    if clean.startswith("none") or "strong" in clean or "excellent" in clean:
        return "✅ <span style='color:#34D399; font-weight:700;'>Optimal</span>"
    return "❌ <span style='color:#F87171; font-weight:700;'>Flaw Detected</span>"

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
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Plus Jakarta Sans', sans-serif; background-color: #090d16; color: #ffffff; margin: 0; padding: 24px; }}
            .glass-card {{ background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }}
            .toolbar-btn {{ transition: all 0.15s ease; cursor: pointer; border: 1px solid rgba(255,255,255,0.08); }}
            .toolbar-btn.active {{ background: linear-gradient(135deg, #4F46E5, #7C3AED); color: #ffffff; border-color: transparent; }}
            .toolbar-btn:not(.active) {{ background: rgba(255,255,255,0.05); color: #94A3B8; }}
            #original-{variant_id} {{ display: none; }}
            #heatmap-{variant_id} {{ opacity: 0; pointer-events: none; transition: opacity 0.35s ease; }}
            .heat-zone {{ position: absolute; border-radius: 18px; mix-blend-mode: screen; }}
            .heat-label {{
                position: absolute; font-size: 10px; font-weight: 800; letter-spacing: 0.04em;
                padding: 3px 9px; border-radius: 999px; background: rgba(0,0,0,0.6); backdrop-filter: blur(2px);
                white-space: nowrap;
            }}
        </style>
    </head>
    <body>
        <div class="max-w-4xl mx-auto mb-4 flex flex-wrap items-center justify-center gap-2">
            <button id="btn-redesign-{variant_id}" class="toolbar-btn active text-xs font-bold px-4 py-2 rounded-lg" onclick="showView('{variant_id}','redesign')">✨ AI Redesign</button>
            <button id="btn-original-{variant_id}" class="toolbar-btn text-xs font-bold px-4 py-2 rounded-lg" onclick="showView('{variant_id}','original')">📝 Original</button>
            <button id="btn-heat-{variant_id}" class="toolbar-btn text-xs font-bold px-4 py-2 rounded-lg" onclick="toggleHeatmap('{variant_id}')">🔥 Attention Heatmap</button>
        </div>

        <div class="relative max-w-4xl mx-auto">
            <div id="redesign-{variant_id}" class="relative glass-card rounded-3xl p-10 md:p-14 shadow-2xl overflow-hidden">
                <div class="relative z-10 text-center">
                    <span class="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/25 text-indigo-300 text-xs font-bold px-4 py-1.5 rounded-full mb-6 uppercase">
                        ✨ {badge}
                    </span>
                    <h1 class="text-4xl md:text-6xl font-extrabold tracking-tight text-white mb-6 leading-tight">{headline}</h1>
                    <p class="text-slate-300 text-base md:text-xl mb-8 max-w-2xl mx-auto leading-relaxed">{subheadline}</p>
                    <div class="flex flex-col sm:flex-row gap-4 justify-center items-center mb-10">
                        <button class="w-full sm:w-auto bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold px-9 py-4 rounded-xl shadow-lg">{cta_primary}</button>
                        <button class="w-full sm:w-auto bg-slate-800/80 text-slate-200 font-bold px-8 py-4 rounded-xl border border-slate-700">{cta_secondary}</button>
                    </div>
                    <p class="text-xs text-slate-400 font-medium">{social_proof}</p>
                </div>

                <div id="heatmap-{variant_id}" class="absolute inset-0 z-20">
                    <div class="heat-zone" style="top:13%; left:12%; width:76%; height:23%; background:radial-gradient(ellipse at center, rgba(239,68,68,0.55), rgba(239,68,68,0) 70%);"></div>
                    <span class="heat-label" style="top:15%; left:50%; transform:translateX(-50%); color:#FCA5A5;">🔴 65% Headline Focus</span>
                    <div class="heat-zone" style="top:57%; left:28%; width:44%; height:17%; background:radial-gradient(ellipse at center, rgba(250,204,21,0.5), rgba(250,204,21,0) 70%);"></div>
                    <span class="heat-label" style="top:63%; left:50%; transform:translateX(-50%); color:#FDE68A;">🟡 25% CTA Focus</span>
                </div>
            </div>

            <div id="original-{variant_id}" class="relative bg-white rounded-2xl p-10 md:p-14 shadow-2xl text-center" style="font-family: Arial, sans-serif;">
                <span class="inline-block bg-gray-100 text-gray-500 text-xs font-semibold px-3 py-1 rounded mb-4 uppercase">Before — Unoptimized</span>
                <h1 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">{before_headline}</h1>
                <p class="text-gray-600 text-sm md:text-base mb-8 max-w-2xl mx-auto">{before_body}</p>
                <button class="bg-gray-700 text-white text-sm font-medium px-6 py-2 rounded">Submit</button>
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

# Render Scorecards
def render_single_scorecard(main):
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.metric("Conversion Health Score", f"{main['orig_score']} / 100")
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
        st.subheader("🔍 Breakdown & Flaw Diagnosis")
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
    st.subheader("🏆 Winner & Gap Analysis")
    if winner == "yours":
        st.markdown(f'<span class="winner-badge">🏆 You win by {gap} points</span>', unsafe_allow_html=True)
    elif winner == "competitor":
        st.markdown(f'<span class="loser-badge">⚠️ Competitor leads by {gap} points</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="tag-pill">🤝 Dead heat — scores are tied</span>', unsafe_allow_html=True)
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
        user_input = st.text_area("🟦 Your website or pitch:", height=140, key="user_input_battle")
    with col_in2:
        competitor_input = st.text_area("🟥 Competitor website or pitch:", height=140, key="competitor_input_battle")
else:
    user_input = st.text_area("Paste product pitch OR website URL below:", height=120, key="user_input_single")
    competitor_input = ""

analyze_button = st.button("🚀 Analyze & Auto-Redesign Live", type="primary")

# Execute Analysis & Save in Session State
if analyze_button:
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    elif battle_mode and (not user_input.strip() or not competitor_input.strip()):
        st.warning("Please fill in both fields for Battle Mode.")
    elif not battle_mode and not user_input.strip():
        st.warning("Please enter text or a URL.")
    else:
        with st.spinner("Analyzing psychological hooks and generating high-converting UI..."):
            genai.configure(api_key=api_key)
            available_models = get_available_models()

            processed_main, is_url_main, scrape_failed_main = process_input(user_input)
            if scrape_failed_main:
                st.warning("⚠️ Could not scrape URL automatically (site blocked bot). Analyzing URL string directly.")

            raw_data_main, model_main = run_gemini_analysis(processed_main, available_models)

            if raw_data_main is None:
                st.error("❌ Failed to fetch AI response. Please check API key/quota.")
            else:
                main = normalize_data(raw_data_main)
                main["used_model"] = model_main
                before_main = build_before_snapshot(user_input, processed_main, is_url_main)

                comp = None
                before_comp = None
                if battle_mode:
                    processed_comp, is_url_comp, scrape_failed_comp = process_input(competitor_input)
                    raw_data_comp, model_comp = run_gemini_analysis(processed_comp, available_models)
                    if raw_data_comp:
                        comp = normalize_data(raw_data_comp)
                        comp["used_model"] = model_comp
                        before_comp = build_before_snapshot(competitor_input, processed_comp, is_url_comp)

                # Save into Session State to prevent loss on reruns
                st.session_state['has_data'] = True
                st.session_state['main'] = main
                st.session_state['before_main'] = before_main
                st.session_state['comp'] = comp
                st.session_state['before_comp'] = before_comp
                st.session_state['battle_mode'] = battle_mode

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
                st.components.v1.html(render_hero_preview(main, before_main, "main"), height=700, scrolling=True)
            with c2:
                st.markdown('<span class="site-label-red">🟥 COMPETITOR</span>', unsafe_allow_html=True)
                st.components.v1.html(render_hero_preview(comp, before_comp, "comp"), height=700, scrolling=True)
        else:
            st.components.v1.html(render_hero_preview(main, before_main, "main"), height=700, scrolling=True)

    with tab3:
        st.subheader("💻 Ready-to-Use Tailwind HTML")
        st.code(render_hero_preview(main, before_main, "main"), language="html")

import streamlit as st
import google.generativeai as genai
import json
import re
import html as html_lib
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

    /* Battle Mode Additions */
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
    .vs-divider {
        text-align: center;
        font-weight: 900;
        font-size: 1.1rem;
        color: #475569;
        letter-spacing: 0.15em;
        margin: 8px 0 20px 0;
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

    /* CRO Academy */
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

# ──────────────────────────────────────────────────────────────────────────
# CRO Academy — static, always-visible teaching section (no API key needed)
# ──────────────────────────────────────────────────────────────────────────
ACADEMY_LESSONS = [
    ("🔍 Clarity", "Visitors decide whether to keep reading within seconds. If a headline describes a "
     "feature instead of the outcome a person gets, the brain has to do extra translation work — and most "
     "people simply leave instead of doing it."),
    ("🎁 Benefit Framing", "People don't buy tools, they buy outcomes: time saved, stress removed, money "
     "earned. Copy that lists specs reads as a catalog; copy that names the transformation reads as a reason "
     "to act."),
    ("⏳ Urgency & Scarcity", "Decision-making research (popularized by Robert Cialdini's work on persuasion) "
     "shows people act faster when a moment feels limited or timely. A generic 'Submit' button asks for effort "
     "with nothing in return; a specific, time-bound CTA gives a reason to click now."),
    ("🧠 Cognitive Friction", "Every extra decision, unclear label, or vague next step adds mental load. Lower "
     "friction doesn't mean fewer words — it means the next step is obvious at a glance."),
    ("👁️ Visual Attention (F-Pattern)", "Eye-tracking studies from researchers like Nielsen Norman Group have "
     "repeatedly found that visitors scan pages in predictable patterns, spending most of their attention on "
     "the headline and hero area before decaying sharply. That's the real research behind this tool's simulated "
     "heatmap."),
]

with st.expander("🎓 CRO Academy — The Psychology Powering This Tool (start here, no API key needed)", expanded=False):
    st.caption("SiteGlow AI isn't just a scoring tool — it's built to teach you *why* each principle below moves the needle, then shows the fix on your own copy.")
    for title, body in ACADEMY_LESSONS:
        st.markdown(
            f'<div class="lesson-card"><div class="lesson-title">{title}</div>'
            f'<div class="lesson-body">{body}</div></div>',
            unsafe_allow_html=True
        )

# ──────────────────────────────────────────────────────────────────────────
# Helper Function: Web Scraper for Live URLs
# ──────────────────────────────────────────────────────────────────────────
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


def process_input(raw_text):
    """Returns (processed_copy, is_url) — scrapes if a URL, else passes text through."""
    text = (raw_text or "").strip()
    if text.startswith("http://") or text.startswith("https://"):
        st.info(f"🌐 Scraping content from `{text}`...")
        return extract_website_content(text), True
    return text, False


def build_before_snapshot(raw_input, processed_copy, is_url):
    """Builds a plain-text 'before' snapshot used to render the un-optimized hero."""
    if is_url:
        title_match = re.search(r'Page Title:\s*(.*)', processed_copy)
        meta_match = re.search(r'Meta Description:\s*(.*)', processed_copy)
        headline = title_match.group(1).strip() if title_match and title_match.group(1).strip() else "Untitled Page"
        body = meta_match.group(1).strip() if meta_match and meta_match.group(1).strip() else processed_copy[:220]
    else:
        sentences = [s.strip() for s in re.split(r'[.\n]', raw_input) if s.strip()]
        headline = sentences[0][:120] if sentences else (raw_input[:120] if raw_input else "Your Original Headline")
        body = raw_input[:280] if raw_input else "No original copy supplied."

    if not headline:
        headline = "Your Original Headline"
    if not body:
        body = "No original copy supplied."

    return {"headline": headline, "body": body}


def esc(value):
    """HTML-escape any value before it goes into an f-string HTML template."""
    return html_lib.escape(str(value), quote=True)


# ──────────────────────────────────────────────────────────────────────────
# Gemini Engine Helpers
# ──────────────────────────────────────────────────────────────────────────
def get_available_models():
    all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

    priority_list = [
        "models/gemini-3.6-flash",
        "models/gemini-3.5-flash",
        "models/gemini-3.1-pro-preview",
        "models/gemini-3.1-flash-lite",
        "models/gemini-flash-latest",
        "models/gemini-pro-latest"
    ]

    return [m for m in priority_list if m in all_models] + [m for m in all_models if m not in priority_list]


def build_prompt(processed_copy):
    return f"""
    You are a world-class CRO (Conversion Rate Optimization) strategist and senior SaaS visual designer.
    Analyze this business copy/content: "{processed_copy}"

    EVALUATION & SCORING RULES:
    1. Assign a float score from 15.0 to 99.0 based on how outcome-driven, clear, and compelling it is.
    2. If an element (Headline, Value Prop, CTA) is ALREADY exceptional, set flaw text starting with "None — " (e.g., "None — Headline is outcome-focused and high-impact.").
    3. Rewrite the messaging into a stunning, ultra-high-converting Hero block section.
    4. Provide detailed rating scores (0-100) for Clarity, Urgency, Benefit Alignment, and Friction.
    5. You are also acting as a CRO TUTOR. For each flaw, alongside the flaw text, provide a one-sentence
       "lesson" field explaining the general psychological or UX principle at play — written so a beginner
       marketer would learn something transferable, not just get a fix for this one page.

    Return ONLY a JSON object strictly matching this schema:
    {{
        "original_score": 42.5,
        "clarity_score": 50,
        "urgency_score": 30,
        "benefit_score": 40,
        "friction_score": 80,
        "headline_flaw": "Describes what you built (a commodity feature) instead of what the user gains.",
        "headline_lesson": "Headlines convert better when they state the outcome the reader gets, not the feature you shipped.",
        "value_prop_flaw": "Lacks specific outcome metrics, time-saved claims, or emotional transformation.",
        "value_prop_lesson": "Specific, quantified outcomes are more persuasive than vague claims because they feel provable.",
        "cta_flaw": "Generic, low-urgency button text with zero value proposition.",
        "cta_lesson": "A CTA that names the next concrete step and a reason to act now outperforms passive verbs like 'Submit'.",
        "badge_text": "AUTOMATED WORKFLOWS",
        "social_proof": "⚡ Trusted by 10,000+ high-growth teams",
        "rewritten_headline": "Bring Your Remote Team into Perfect Alignment",
        "rewritten_subheadline": "Stop losing tasks across fragmented chats. Unify execution, decision-making, and communication in one fast dashboard.",
        "cta_primary": "Start Free 14-Day Trial →",
        "cta_secondary": "Watch 2-Min Product Tour"
    }}
    Do not write introductory or markdown commentary outside JSON.
    """


def run_gemini_analysis(processed_copy, available_models):
    """Runs the prompt against the first working model. Returns (data_dict_or_None, used_model_or_None)."""
    prompt = build_prompt(processed_copy)
    response = None
    used_model = None

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
        return None, None

    # Robust JSON Extraction
    json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
    if not json_match:
        return None, None

    try:
        data = json.loads(json_match.group(0))
    except Exception:
        return None, None

    return data, used_model


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
        "headline_lesson": data.get("headline_lesson", "Headlines convert better when they state the outcome the reader gets, not the feature you shipped."),
        "value_flaw": data.get("value_prop_flaw", "Lists commodity features without highlighting emotional stakes."),
        "value_lesson": data.get("value_prop_lesson", "Specific, quantified outcomes are more persuasive than vague claims because they feel provable."),
        "cta_flaw": data.get("cta_flaw", "Low-energy CTA with minimal incentive to click."),
        "cta_lesson": data.get("cta_lesson", "A CTA that names the next concrete step and a reason to act now outperforms passive verbs like 'Submit'."),
        "badge": data.get("badge_text", "AI WORKFLOW ENGINE"),
        "social_proof": data.get("social_proof", "⚡ Loved by 5,000+ founders"),
        "headline": data.get("rewritten_headline", "Eliminate Chaos & Scale Execution"),
        "subheadline": data.get("rewritten_subheadline", "Stop jumping between endless tabs. Streamline collaboration with an intelligent workspace."),
        "cta_primary": data.get("cta_primary", "Get Started Free →"),
        "cta_secondary": data.get("cta_secondary", "View Live Demo"),
    }


def get_status_badge(flaw_text):
    clean = flaw_text.strip().lower()
    if clean.startswith("none") or "strong" in clean or "excellent" in clean or "catchy" in clean:
        return "✅ <span style='color:#34D399; font-weight:700;'>Optimal</span>"
    return "❌ <span style='color:#F87171; font-weight:700;'>Flaw Detected</span>"


def compute_winner(main, comp):
    """Compares two normalized data dicts and returns (winner, gap, breakdown_rows)."""
    main_score = main["orig_score"]
    comp_score = comp["orig_score"]

    if main_score > comp_score:
        winner = "yours"
    elif comp_score > main_score:
        winner = "competitor"
    else:
        winner = "tie"

    gap = round(abs(main_score - comp_score), 1)

    sub_metrics = [
        ("Message Clarity", main["clarity"], comp["clarity"], True),
        ("Benefit Alignment", main["benefit"], comp["benefit"], True),
        ("CTA Urgency", main["urgency"], comp["urgency"], True),
        ("Friction (lower is better)", main["friction"], comp["friction"], False),
    ]

    breakdown = []
    for label, m_val, c_val, higher_is_better in sub_metrics:
        if higher_is_better:
            side_winner = "yours" if m_val > c_val else ("competitor" if c_val > m_val else "tie")
        else:
            side_winner = "yours" if m_val < c_val else ("competitor" if c_val < m_val else "tie")
        metric_gap = abs(m_val - c_val)
        breakdown.append((label, m_val, c_val, side_winner, metric_gap))

    biggest = max(breakdown, key=lambda row: row[4]) if breakdown else None

    return winner, gap, breakdown, biggest


# ──────────────────────────────────────────────────────────────────────────
# Live Hero Preview: Before/After Toggle + Simulated Attention Heatmap
# ──────────────────────────────────────────────────────────────────────────
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
                            🚀 Live Application Dashboard Mockup
                        </div>
                    </div>
                </div>

                <!-- Simulated AI Attention Heatmap Overlay -->
                <div id="heatmap-{variant_id}" class="absolute inset-0 z-20">
                    <div class="heat-zone" style="top:13%; left:12%; width:76%; height:23%; background:radial-gradient(ellipse at center, rgba(239,68,68,0.55), rgba(239,68,68,0) 70%);"></div>
                    <span class="heat-label" style="top:15%; left:50%; transform:translateX(-50%); color:#FCA5A5;">🔴 65% Headline</span>

                    <div class="heat-zone" style="top:57%; left:28%; width:44%; height:17%; background:radial-gradient(ellipse at center, rgba(250,204,21,0.5), rgba(250,204,21,0) 70%);"></div>
                    <span class="heat-label" style="top:63%; left:50%; transform:translateX(-50%); color:#FDE68A;">🟡 25% CTA</span>

                    <div class="heat-zone" style="top:83%; left:18%; width:64%; height:15%; background:radial-gradient(ellipse at center, rgba(34,197,94,0.4), rgba(34,197,94,0) 70%);"></div>
                    <span class="heat-label" style="top:88%; left:50%; transform:translateX(-50%); color:#86EFAC;">🟢 10% Nav / Footer</span>
                </div>
            </div>

            <div id="original-{variant_id}" class="relative bg-white rounded-2xl p-10 md:p-14 shadow-2xl text-center" style="font-family: Arial, Helvetica, sans-serif;">
                <span class="inline-block bg-gray-100 text-gray-500 text-xs font-semibold px-3 py-1 rounded mb-4 uppercase tracking-wide">Before — Unoptimized</span>
                <h1 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">{before_headline}</h1>
                <p class="text-gray-600 text-sm md:text-base mb-8 max-w-2xl mx-auto">{before_body}</p>
                <button class="bg-gray-700 text-white text-sm font-medium px-6 py-2 rounded">Submit</button>
                <p class="text-xs text-gray-400 mt-6">No urgency cue · No social proof · Generic call-to-action</p>
            </div>

        </div>

        <script>
            function showView(id, view) {{
                document.getElementById('redesign-' + id).style.display = (view === 'redesign') ? 'block' : 'none';
                document.getElementById('original-' + id).style.display = (view === 'original') ? 'block' : 'none';
                document.getElementById('btn-redesign-' + id).classList.toggle('active', view === 'redesign');
                document.getElementById('btn-original-' + id).classList.toggle('active', view === 'original');
                if (view === 'original') {{
                    document.getElementById('heatmap-' + id).style.opacity = '0';
                    document.getElementById('btn-heat-' + id).classList.remove('active');
                }}
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


# ──────────────────────────────────────────────────────────────────────────
# Scorecard Renderers (Tab 1)
# ──────────────────────────────────────────────────────────────────────────
def render_single_scorecard(main):
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        potential_boost = round(max(0.0, 98.0 - main["orig_score"]), 1)
        st.metric("Conversion Health Score", f"{main['orig_score']} / 100", delta=f"+{potential_boost}% Estimated Lift", delta_color="normal")
        st.caption(f"Engine Model: `{main['used_model']}`")
        st.write("---")

        if main["orig_score"] >= 82.0:
            st.success("🎉 **High-Converting Messaging!** Clear positioning with strong user value.")
        elif main["orig_score"] >= 60.0:
            st.info("💡 **Good Foundation.** Minor messaging tweaks needed to eliminate hesitation.")
        else:
            st.warning("⚠️ **High Bounce Rate Risk.** Pitch is feature-centric and lacks immediate value.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.subheader("🧠 CRO Psychological Breakdown")
        st.write(f"**Message Clarity:** {main['clarity']}/100")
        st.progress(main["clarity"] / 100)
        st.write(f"**Value/Benefit Focus:** {main['benefit']}/100")
        st.progress(main["benefit"] / 100)
        st.write(f"**Call-to-Action Urgency:** {main['urgency']}/100")
        st.progress(main["urgency"] / 100)
        st.write(f"**Friction Level (Lower is better):** {main['friction']}/100")
        st.progress(main["friction"] / 100)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.subheader("🔍 Breakdown & Flaw Diagnosis")

        st.markdown(f"#### {get_status_badge(main['headline_flaw'])} Headline Structure", unsafe_allow_html=True)
        st.write(main["headline_flaw"])
        st.markdown(f'<div class="principle-line">🎓 <b>Principle:</b> {esc(main["headline_lesson"])}</div>', unsafe_allow_html=True)
        st.write("---")

        st.markdown(f"#### {get_status_badge(main['value_flaw'])} Value Proposition & Benefits", unsafe_allow_html=True)
        st.write(main["value_flaw"])
        st.markdown(f'<div class="principle-line">🎓 <b>Principle:</b> {esc(main["value_lesson"])}</div>', unsafe_allow_html=True)
        st.write("---")

        st.markdown(f"#### {get_status_badge(main['cta_flaw'])} Call-To-Action (CTA)", unsafe_allow_html=True)
        st.write(main["cta_flaw"])
        st.markdown(f'<div class="principle-line">🎓 <b>Principle:</b> {esc(main["cta_lesson"])}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def render_mini_breakdown(label_prefix, data):
    st.write(f"**Message Clarity:** {data['clarity']}/100")
    st.progress(data["clarity"] / 100)
    st.write(f"**Value/Benefit Focus:** {data['benefit']}/100")
    st.progress(data["benefit"] / 100)
    st.write(f"**CTA Urgency:** {data['urgency']}/100")
    st.progress(data["urgency"] / 100)
    st.write(f"**Friction (Lower is better):** {data['friction']}/100")
    st.progress(data["friction"] / 100)


METRIC_LESSON_MAP = {
    "Message Clarity": "headline_lesson",
    "Benefit Alignment": "value_lesson",
    "CTA Urgency": "cta_lesson",
}
FRICTION_FALLBACK_LESSON = ("Lower friction doesn't mean fewer words — it means the next step is obvious at a "
                             "glance, with nothing making a visitor pause to figure out what to do.")


def render_battle_scorecard(main, comp):
    winner, gap, breakdown, biggest = compute_winner(main, comp)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<span class="site-label-blue">🟦 YOUR SITE</span>', unsafe_allow_html=True)
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.metric("Conversion Health Score", f"{main['orig_score']} / 100")
        st.caption(f"Engine Model: `{main['used_model']}`")
        st.write("---")
        render_mini_breakdown("Yours", main)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<span class="site-label-red">🟥 COMPETITOR</span>', unsafe_allow_html=True)
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.metric("Conversion Health Score", f"{comp['orig_score']} / 100")
        st.caption(f"Engine Model: `{comp['used_model']}`")
        st.write("---")
        render_mini_breakdown("Competitor", comp)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("🏆 Winner & Gap Analysis")

    if winner == "yours":
        st.markdown(f'<span class="winner-badge">🏆 You win by {gap} points</span>', unsafe_allow_html=True)
        st.write("Your messaging currently out-converts the competitor's on the metrics analyzed below.")
    elif winner == "competitor":
        st.markdown(f'<span class="loser-badge">⚠️ Competitor leads by {gap} points</span>', unsafe_allow_html=True)
        st.write("The competitor's page is currently the stronger conversion machine — see the gaps below.")
    else:
        st.markdown('<span class="tag-pill">🤝 Dead heat — scores are tied</span>', unsafe_allow_html=True)

    st.write("")
    for label, m_val, c_val, side_winner, _metric_gap in breakdown:
        if side_winner == "yours":
            icon = "🟦"
        elif side_winner == "competitor":
            icon = "🟥"
        else:
            icon = "⚪"
        st.write(f"{icon} **{label}** — Yours: `{m_val}` · Competitor: `{c_val}`")

    # Synthesized teaching takeaway from whichever metric had the widest gap — no extra API call
    if biggest is not None and biggest[3] != "tie":
        label, m_val, c_val, side_winner, _gap_val = biggest
        source_data = main if side_winner == "yours" else comp
        lesson_key = METRIC_LESSON_MAP.get(label)
        lesson_text = source_data.get(lesson_key, FRICTION_FALLBACK_LESSON) if lesson_key else FRICTION_FALLBACK_LESSON
        st.markdown(
            f'<div class="principle-line">🎓 <b>Key Lesson:</b> the widest gap was in <b>{esc(label)}</b> — '
            f'{esc(lesson_text)}</div>',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("🔍 Full Flaw Diagnosis & Principles — Your Site"):
        st.markdown(f"**Headline:** {main['headline_flaw']}")
        st.caption(f"🎓 {main['headline_lesson']}")
        st.markdown(f"**Value Proposition:** {main['value_flaw']}")
        st.caption(f"🎓 {main['value_lesson']}")
        st.markdown(f"**CTA:** {main['cta_flaw']}")
        st.caption(f"🎓 {main['cta_lesson']}")

    with st.expander("🔍 Full Flaw Diagnosis & Principles — Competitor"):
        st.markdown(f"**Headline:** {comp['headline_flaw']}")
        st.caption(f"🎓 {comp['headline_lesson']}")
        st.markdown(f"**Value Proposition:** {comp['value_flaw']}")
        st.caption(f"🎓 {comp['value_lesson']}")
        st.markdown(f"**CTA:** {comp['cta_flaw']}")
        st.caption(f"🎓 {comp['cta_lesson']}")


# ──────────────────────────────────────────────────────────────────────────
# Sidebar Setup
# ──────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Engine Setup")
    raw_api_key = st.text_input("Enter Gemini API Key:", type="password")
    api_key = raw_api_key.strip() if raw_api_key else ""
    st.markdown("[Get a free key from Google AI Studio](https://aistudio.google.com/)")
    st.divider()
    st.caption("Powered by Gemini 3.6 Flash Engine")
    st.caption("🎓 CRO Tutor · 🥊 Battle Mode · 🔥 Attention Heatmap · 📝 Before/After")

# ──────────────────────────────────────────────────────────────────────────
# Input Interface
# ──────────────────────────────────────────────────────────────────────────
battle_mode = st.toggle("🥊 Enable Competitor CRO Battle Mode", value=False,
                         help="Paste your site and a competitor's side-by-side to see who converts better.")

if battle_mode:
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        user_input = st.text_area(
            "🟦 Your website or pitch:",
            height=140,
            placeholder="e.g. https://yourproduct.com OR paste your pitch copy...",
            key="user_input_battle"
        )
    with col_in2:
        competitor_input = st.text_area(
            "🟥 Competitor website or pitch:",
            height=140,
            placeholder="e.g. https://competitor.com OR paste their pitch copy...",
            key="competitor_input_battle"
        )
else:
    user_input = st.text_area(
        "Paste product pitch OR website URL below:",
        height=120,
        placeholder="e.g. https://stripe.com OR 'We built a messaging tool for remote teams. You can send chats and share files easily...'",
        key="user_input_single"
    )
    competitor_input = ""

button_label = "🥊 Run CRO Battle Analysis" if battle_mode else "🚀 Analyze & Auto-Redesign Live"
analyze_button = st.button(button_label, type="primary")

if analyze_button:
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    elif battle_mode and (not user_input.strip() or not competitor_input.strip()):
        st.warning("Please paste content or a URL for both Your Website and the Competitor Website.")
    elif not battle_mode and not user_input.strip():
        st.warning("Please paste some pitch text or a website URL first.")
    else:
        spinner_msg = "Running head-to-head CRO battle analysis..." if battle_mode else "Analyzing psychological hooks and generating high-converting UI..."
        with st.spinner(spinner_msg):
            try:
                genai.configure(api_key=api_key)
                available_models = get_available_models()

                if not available_models:
                    st.error("❌ No content models available for this API key.")
                    st.stop()

                # ── Analyze "Your Site" ──
                processed_main, is_url_main = process_input(user_input)
                raw_data_main, model_main = run_gemini_analysis(processed_main, available_models)

                if raw_data_main is None:
                    st.error("❌ Failed to fetch AI response for your site. Please verify key quota.")
                    st.stop()

                main = normalize_data(raw_data_main)
                main["used_model"] = model_main
                before_main = build_before_snapshot(user_input, processed_main, is_url_main)

                # ── Analyze "Competitor" (Battle Mode only) ──
                comp = None
                before_comp = None
                if battle_mode:
                    processed_comp, is_url_comp = process_input(competitor_input)
                    raw_data_comp, model_comp = run_gemini_analysis(processed_comp, available_models)

                    if raw_data_comp is None:
                        st.error("❌ Failed to fetch AI response for the competitor site. Please verify key quota.")
                        st.stop()

                    comp = normalize_data(raw_data_comp)
                    comp["used_model"] = model_comp
                    before_comp = build_before_snapshot(competitor_input, processed_comp, is_url_comp)

                # ── Render Tabs ──
                tab_labels = ["📊 CRO Intelligence Scorecard", "✨ Live Hero Redesign", "💻 Export Code & Implement"]
                tab1, tab2, tab3 = st.tabs(tab_labels)

                with tab1:
                    if battle_mode:
                        render_battle_scorecard(main, comp)
                    else:
                        render_single_scorecard(main)

                with tab2:
                    st.subheader("✨ Live Hero Redesign")
                    st.caption("Toggle between your original copy and the AI-optimized redesign. Click 🔥 to reveal the simulated visitor attention heatmap.")

                    if battle_mode:
                        col_p1, col_p2 = st.columns(2)
                        with col_p1:
                            st.markdown('<span class="site-label-blue">🟦 YOUR SITE</span>', unsafe_allow_html=True)
                            main_hero_html = render_hero_preview(main, before_main, "main")
                            st.components.v1.html(main_hero_html, height=700, scrolling=True)
                        with col_p2:
                            st.markdown('<span class="site-label-red">🟥 COMPETITOR</span>', unsafe_allow_html=True)
                            comp_hero_html = render_hero_preview(comp, before_comp, "comp")
                            st.components.v1.html(comp_hero_html, height=700, scrolling=True)
                    else:
                        main_hero_html = render_hero_preview(main, before_main, "main")
                        st.components.v1.html(main_hero_html, height=700, scrolling=True)

                with tab3:
                    st.subheader("💻 Ready-to-Use Tailwind HTML")
                    st.caption("Copy and paste this code straight into Framer, Webflow, React, or standard HTML.")

                    if battle_mode:
                        export_choice = st.radio("Which redesign do you want to export?", ["🟦 Your Site", "🟥 Competitor"], horizontal=True)
                        if export_choice == "🟦 Your Site":
                            st.code(main_hero_html, language="html")
                        else:
                            st.code(comp_hero_html, language="html")
                    else:
                        st.code(main_hero_html, language="html")

            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

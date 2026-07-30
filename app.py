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

    /* Self-contained score card pieces (built as one HTML block, not split across widgets) */
    .score-value { font-size: 2.4rem; font-weight: 900; color: #818CF8; line-height: 1.1; margin: 4px 0 2px 0; }
    .score-sub { font-size: 0.85rem; color: #94A3B8; margin-bottom: 14px; }
    .model-caption { font-size: 0.78rem; color: #6B7280; font-family: monospace; margin-bottom: 14px; }
    .metric-row { margin-bottom: 12px; }
    .metric-label { font-size: 0.9rem; color: #E5E7EB; font-weight: 600; margin-bottom: 4px; }
    .bar-track { background: #1F2937; border-radius: 999px; height: 9px; overflow: hidden; }
    .bar-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #4F46E5, #A855F7); }
    .status-optimal { color: #34D399; font-weight: 800; }
    .status-flaw { color: #F87171; font-weight: 800; }
    .diagnosis-heading { font-size: 1.05rem; font-weight: 800; color: #F3F4F6; margin: 14px 0 4px 0; }
    .diagnosis-body { color: #D1D5DB; font-size: 0.92rem; margin-bottom: 4px; }
    .callout-banner {
        border-radius: 12px;
        padding: 12px 16px;
        font-size: 0.9rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .callout-success { background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35); color: #6EE7B7; }
    .callout-info { background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.35); color: #A5B4FC; }
    .callout-warning { background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35); color: #FCD34D; }
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
    7. Also write a SECOND, genuinely different hero tagline (a different emotional angle — e.g. speed vs. trust vs. simplicity vs. ambition).
       Both taglines must be equally strong and usable on their own; the second is an alternative angle, not a weaker backup.
    8. Act as a real eye-tracking / attention-mapping analyst. Estimate how visitor attention would realistically distribute across the
       REWRITTEN hero's four zones — Headline, Subheadline, Primary CTA, Social Proof — based on THIS SPECIFIC copy's length, specificity,
       contrast and action-orientation. This must NOT be a fixed template split; it must genuinely vary with the copy:
       - A short, punchy, high-contrast headline paired with a weak/generic CTA should skew heavily toward headline attention.
       - A longer headline paired with a sharp, specific, action-verb CTA should show more balanced or CTA-leaning attention.
       - Strong quantified social proof (numbers, named counts) earns more attention share than vague/absent proof.
       The four attention_*_pct values MUST be integers that sum to exactly 100.
       Provide a 2-3 sentence attention_rationale grounded in the specific words you wrote (not generic CRO theory).

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
        "alt_headline": "The Fastest Way Your Team Ships Without the Chaos",
        "alt_subheadline": "A different angle on the same promise — for teams who'd rather move fast than manage more tools.",
        "cta_primary": "Start Free 14-Day Trial",
        "cta_secondary": "Watch 2-Min Demo",
        "attention_headline_pct": 44,
        "attention_subheadline_pct": 16,
        "attention_cta_pct": 29,
        "attention_proof_pct": 11,
        "attention_rationale": "The headline leads with a concrete outcome in high-contrast type, so it captures the dominant share of first-glance attention. The CTA uses a specific, urgent action verb rather than a generic label, pulling meaningfully above baseline. The subheadline and social proof receive brief dwell time typical of F-pattern scan decay."
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
                if not isinstance(data, dict):
                    # Model returned valid JSON but not an object (e.g. a list or bare value) — not usable, try the next model.
                    continue
                return data, model_name
        except Exception:
            time.sleep(0.5)
            continue
    return None, None

def compute_fallback_attention(headline, subheadline, cta_primary, social_proof):
    """
    Content-aware fallback attention split. Only used if the AI response is missing/invalid
    attention fields — but it still reads the ACTUAL generated copy rather than returning a
    fixed constant, so the heatmap never collapses back to a single hardcoded split.
    """
    headline = headline or ""
    subheadline = subheadline or ""
    cta_primary = cta_primary or ""
    social_proof = social_proof or ""

    h_words = max(len(headline.split()), 1)
    sh_words = max(len(subheadline.split()), 1)
    cta_words = max(len(cta_primary.split()), 1)

    strong_cta_verbs = ["free", "now", "start", "get", "instant", "today", "try", "join", "claim", "unlock"]
    cta_has_urgency = any(w in cta_primary.lower() for w in strong_cta_verbs)
    proof_has_numbers = bool(re.search(r'\d', social_proof))

    # Shorter, punchier headlines dominate attention more; long headlines dilute it.
    headline_w = 46 - min(h_words, 16) * 1.3
    subheadline_w = 11 + min(sh_words, 20) * 0.35
    cta_w = 18 + (9 if cta_has_urgency else 0) - min(cta_words, 6) * 0.6
    proof_w = 8 + (6 if proof_has_numbers else 0) + min(len(social_proof) // 15, 4)

    weights = [max(headline_w, 8), max(subheadline_w, 6), max(cta_w, 8), max(proof_w, 5)]
    total = sum(weights)
    pcts = [round(w / total * 100) for w in weights]
    diff = 100 - sum(pcts)
    pcts[0] += diff  # correct rounding drift on the dominant zone
    return pcts  # [headline_pct, subheadline_pct, cta_pct, proof_pct]


def normalize_data(data):
    if not isinstance(data, dict):
        # Defensive fallback: never let a non-dict reach .get() calls below, even if something upstream changes.
        data = {}

    try:
        orig_score = round(float(data.get("original_score", 65.0)), 1)
    except Exception:
        orig_score = 65.0

    final_headline = data.get("rewritten_headline", "Eliminate Chaos & Scale Execution")
    final_subheadline = data.get("rewritten_subheadline", "Streamline collaboration with an intelligent workspace.")
    final_cta_primary = data.get("cta_primary", "Get Started Free")
    final_social_proof = data.get("social_proof", "Loved by 5,000+ founders")

    def _as_float(val):
        try:
            return float(val)
        except (TypeError, ValueError):
            return None

    raw_pcts = [
        _as_float(data.get("attention_headline_pct")),
        _as_float(data.get("attention_subheadline_pct")),
        _as_float(data.get("attention_cta_pct")),
        _as_float(data.get("attention_proof_pct")),
    ]

    valid = (
        all(p is not None for p in raw_pcts)
        and all(p >= 0 for p in raw_pcts)
        and 85 <= sum(raw_pcts) <= 115
    )

    if valid:
        total = sum(raw_pcts)
        attn_pcts = [round(p / total * 100) for p in raw_pcts]
        drift = 100 - sum(attn_pcts)
        attn_pcts[0] += drift
    else:
        attn_pcts = compute_fallback_attention(final_headline, final_subheadline, final_cta_primary, final_social_proof)

    attn_rationale = data.get("attention_rationale") or (
        "Estimated from this copy's headline length, CTA specificity, and social-proof strength "
        "(fallback heuristic — the AI engine didn't return an attention rationale for this run)."
    )

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
        "headline": final_headline,
        "subheadline": final_subheadline,
        "alt_headline": data.get("alt_headline", "The Smarter Way To Get This Done"),
        "alt_subheadline": data.get("alt_subheadline", "A different angle on the same promise — built for people who want results, not more busywork."),
        "cta_primary": final_cta_primary,
        "cta_secondary": data.get("cta_secondary", "View Live Demo"),
        "attn_headline": attn_pcts[0],
        "attn_subheadline": attn_pcts[1],
        "attn_cta": attn_pcts[2],
        "attn_proof": attn_pcts[3],
        "attn_rationale": attn_rationale,
    }

def analyze_single_site_task(raw_input, available_models):
    processed_text, is_url, structured_snap, error_msg = process_input(raw_input)
    if error_msg:
        return {"status": "error", "error": error_msg}

    raw_data, used_model = run_gemini_analysis(processed_text, is_url, available_models)

    if raw_data is None:
        return {"status": "error", "error": "Gemini API failed to return structured CRO analysis. Please check your key or rate limits."}

    try:
        norm_data = normalize_data(raw_data)
        norm_data["used_model"] = used_model
    except Exception as e:
        return {"status": "error", "error": f"Received an unexpected response shape from the AI engine ({type(e).__name__}). Please try again."}

    return {
        "status": "success",
        "data": norm_data,
        "before": structured_snap,
        "is_url": is_url
    }

def get_status_badge(flaw_text):
    clean = str(flaw_text).strip().lower()
    if clean.startswith("none") or clean.startswith("optimal") or "strong" in clean or "excellent" in clean:
        return "<span class='status-optimal'>[Optimal]</span>"
    return "<span class='status-flaw'>[Flaw Detected]</span>"


def html_bar(label, value):
    """One self-contained metric row (label + progress bar) as a single HTML fragment."""
    pct = max(0, min(100, value))
    return (
        f'<div class="metric-row">'
        f'<div class="metric-label">{esc(label)}: {value}/100</div>'
        f'<div class="bar-track"><div class="bar-fill" style="width:{pct}%;"></div></div>'
        f'</div>'
    )


def html_diagnosis_block(heading, flaw_text, lesson_text):
    """One self-contained flaw + plain-language principle block."""
    return (
        f'<div class="diagnosis-heading">{get_status_badge(flaw_text)} {esc(heading)}</div>'
        f'<div class="diagnosis-body">{esc(flaw_text)}</div>'
        f'<div class="principle-line"><b>Why it matters:</b> {esc(lesson_text)}</div>'
    )

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

def heat_zone_markup(zone_id, top_pct, pct_value, rgb, label_text):
    """
    Builds one heatmap zone (glow blob + % label) whose SIZE, INTENSITY, and displayed
    percentage all scale with the actual attention share for this specific copy —
    instead of a fixed blob at a fixed percentage.
    """
    pct_value = max(0, min(100, pct_value))
    width = round(42 + (pct_value / 100) * 46, 1)     # 42% - 88% wide
    height = round(10 + (pct_value / 100) * 24, 1)     # 10% - 34% tall
    opacity = round(0.22 + (pct_value / 100) * 0.55, 2)  # 0.22 - 0.77
    left = round((100 - width) / 2, 1)
    r, g, b = rgb

    zone_div = (
        f'<div class="heat-zone" data-zone="{zone_id}" '
        f'style="top:{top_pct}%; left:{left}%; width:{width}%; height:{height}%; '
        f'background:radial-gradient(ellipse at center, rgba({r},{g},{b},{opacity}), rgba({r},{g},{b},0) 70%);"></div>'
    )
    label_span = (
        f'<span class="heat-label" style="top:{top_pct + height / 2 - 2}%; left:50%; transform:translateX(-50%); '
        f'color:rgb({min(r+40,255)},{min(g+60,255)},{min(b+60,255)});">'
        f'<span class="dot" style="background:rgb({r},{g},{b});"></span> {pct_value}% {esc(label_text)}</span>'
    )
    return zone_div + label_span


def render_hero_preview(fields, variant_id):
    badge = esc(fields["badge"])
    headline = esc(fields["headline"])
    subheadline = esc(fields["subheadline"])
    alt_headline = esc(fields.get("alt_headline", fields["headline"]))
    alt_subheadline = esc(fields.get("alt_subheadline", fields["subheadline"]))
    cta_primary = esc(fields["cta_primary"])
    cta_secondary = esc(fields["cta_secondary"])
    social_proof = esc(fields["social_proof"])
    attn_rationale = esc(fields.get("attn_rationale", ""))

    heat_headline = heat_zone_markup("headline", 8, fields.get("attn_headline", 40), (239, 68, 68), "Headline Focus")
    heat_subheadline = heat_zone_markup("subheadline", 40, fields.get("attn_subheadline", 15), (251, 146, 60), "Subheadline Focus")
    heat_cta = heat_zone_markup("cta", 60, fields.get("attn_cta", 30), (250, 204, 21), "CTA Focus")
    heat_proof = heat_zone_markup("proof", 84, fields.get("attn_proof", 15), (56, 189, 248), "Social Proof Focus")

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

            /* Heatmap Overlay */
            #heatmap-{variant_id} {{ opacity: 0; pointer-events: none; transition: opacity 0.35s ease; position: absolute; inset: 0; z-index: 10; }}
            .heat-zone {{ position: absolute; border-radius: 20px; mix-blend-mode: screen; transition: all 0.3s ease; }}
            .heat-label {{
                position: absolute; font-size: 12px; font-weight: 800; letter-spacing: 0.04em;
                padding: 6px 12px; border-radius: 20px; background: rgba(0,0,0,0.8);
                white-space: nowrap; z-index: 11; border: 1px solid rgba(255,255,255,0.1);
            }}
            .dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }}
            .heat-rationale {{
                position: absolute; bottom: 10px; left: 50%; transform: translateX(-50%);
                width: 88%; max-width: 620px; background: rgba(0,0,0,0.82); border: 1px solid rgba(255,255,255,0.12);
                border-radius: 12px; padding: 10px 16px; font-size: 12px; font-weight: 500; line-height: 1.5;
                color: #E5E7EB; text-align: left; z-index: 12;
            }}
            .heat-rationale b {{ color: #A5B4FC; }}
            
            @media (max-width: 600px) {{
                .ai-h1 {{ font-size: 32px; }}
                .ai-buttons {{ flex-direction: column; width: 100%; }}
                .btn-primary, .btn-secondary {{ width: 100%; }}
            }}
        </style>
    </head>
    <body>
        <div class="toolbar">
            <button id="btn-heat-{variant_id}" class="toolbar-btn" onclick="toggleHeatmap('{variant_id}')">Attention Heatmap</button>
            <button id="btn-tagline-{variant_id}" class="toolbar-btn" onclick="toggleTagline('{variant_id}')">🔄 Try Other Pitch</button>
        </div>

        <div class="preview-container">
            <!-- AI REDESIGN -->
            <div id="redesign-{variant_id}" class="ai-view">
                <span class="ai-badge">{badge}</span>
                <div id="tagline-a-{variant_id}" class="tagline-variant">
                    <h1 class="ai-h1">{headline}</h1>
                    <h2 class="ai-h2">{subheadline}</h2>
                </div>
                <div id="tagline-b-{variant_id}" class="tagline-variant" style="display:none;">
                    <h1 class="ai-h1">{alt_headline}</h1>
                    <h2 class="ai-h2">{alt_subheadline}</h2>
                </div>
                <div class="ai-buttons">
                    <button class="btn-primary">{cta_primary}</button>
                    <button class="btn-secondary">{cta_secondary}</button>
                </div>
                <div class="ai-proof">{social_proof}</div>

                <!-- Heatmap Overlay: zone size/intensity/% driven by this copy's AI-estimated attention split -->
                <div id="heatmap-{variant_id}">
                    {heat_headline}
                    {heat_subheadline}
                    {heat_cta}
                    {heat_proof}
                    <div class="heat-rationale"><b>🧠 Why this pattern:</b> {attn_rationale}</div>
                </div>
            </div>
        </div>

        <script>
            function toggleHeatmap(id) {{
                var hm = document.getElementById('heatmap-' + id);
                var isOn = hm.style.opacity === '1';
                hm.style.opacity = isOn ? '0' : '1';
                document.getElementById('btn-heat-' + id).classList.toggle('active', !isOn);
            }}
            function toggleTagline(id) {{
                var a = document.getElementById('tagline-a-' + id);
                var b = document.getElementById('tagline-b-' + id);
                var btn = document.getElementById('btn-tagline-' + id);
                var showingA = a.style.display !== 'none';
                a.style.display = showingA ? 'none' : 'block';
                b.style.display = showingA ? 'block' : 'none';
                btn.classList.toggle('active', showingA);
            }}
        </script>
    </body>
    </html>
    """

def render_export_html(fields):
    """
    Production-ready hero section only: no app toolbar, no heatmap overlay, no tagline-toggle JS,
    no Original-content block. This is what actually gets shipped to a real site, so it stays
    a clean, dependency-light static HTML document.
    """
    badge = esc(fields["badge"])
    headline = esc(fields["headline"])
    subheadline = esc(fields["subheadline"])
    cta_primary = esc(fields["cta_primary"])
    cta_secondary = esc(fields["cta_secondary"])
    social_proof = esc(fields["social_proof"])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{headline}</title>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800;900&display=swap" rel="stylesheet">
<style>
    * {{ box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; margin: 0; padding: 0; }}
    body {{ background-color: #090d16; }}
    .hero {{
        max-width: 900px; margin: 0 auto; background: rgba(17, 24, 39, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 24px; padding: 60px 40px;
        text-align: center; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }}
    .hero-badge {{
        display: inline-block; background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3);
        color: #A5B4FC; font-size: 12px; font-weight: 800; padding: 6px 16px; border-radius: 20px;
        text-transform: uppercase; letter-spacing: 1px; margin-bottom: 24px;
    }}
    .hero-h1 {{ font-size: 42px; font-weight: 900; color: #fff; margin: 0 0 24px 0; line-height: 1.15; letter-spacing: -0.02em; }}
    .hero-h2 {{ font-size: 18px; color: #cbd5e1; margin: 0 auto 32px auto; max-width: 600px; line-height: 1.6; font-weight: 500; }}
    .hero-buttons {{ display: flex; gap: 16px; justify-content: center; margin-bottom: 24px; flex-wrap: wrap; }}
    .btn-primary {{
        background: linear-gradient(135deg, #4F46E5, #7C3AED); color: white; border: none;
        padding: 14px 32px; border-radius: 12px; font-size: 16px; font-weight: 800; cursor: pointer;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4);
    }}
    .btn-secondary {{
        background: rgba(30, 41, 59, 0.8); color: #e2e8f0; border: 1px solid #334155;
        padding: 14px 32px; border-radius: 12px; font-size: 16px; font-weight: 800; cursor: pointer;
    }}
    .hero-proof {{ font-size: 13px; color: #94a3b8; font-weight: 700; }}
    @media (max-width: 600px) {{
        .hero {{ padding: 40px 24px; }}
        .hero-h1 {{ font-size: 32px; }}
        .hero-buttons {{ flex-direction: column; width: 100%; }}
        .btn-primary, .btn-secondary {{ width: 100%; }}
    }}
</style>
</head>
<body>
    <section class="hero">
        <span class="hero-badge">{badge}</span>
        <h1 class="hero-h1">{headline}</h1>
        <h2 class="hero-h2">{subheadline}</h2>
        <div class="hero-buttons">
            <button class="btn-primary">{cta_primary}</button>
            <button class="btn-secondary">{cta_secondary}</button>
        </div>
        <div class="hero-proof">{social_proof}</div>
    </section>
</body>
</html>
"""

def render_single_scorecard(main):
    col1, col2 = st.columns([1, 2])
    with col1:
        if main["orig_score"] >= 82.0:
            callout = '<div class="callout-banner callout-success">🎉 High-Converting! Clear positioning with strong user value.</div>'
        elif main["orig_score"] >= 60.0:
            callout = '<div class="callout-banner callout-info">💡 Good Foundation. A few tweaks would remove hesitation.</div>'
        else:
            callout = '<div class="callout-banner callout-warning">⚠️ High Bounce Risk. Feels feature-first, not outcome-first.</div>'

        left_card = (
            '<div class="card-box">'
            '<div class="card-title">Conversion Health</div>'
            f'<div class="score-value">{main["orig_score"]} / 100</div>'
            '<div class="score-sub">Overall Score</div>'
            f'<div class="model-caption">Engine Model: {esc(main["used_model"])}</div>'
            f'{callout}'
            f'{html_bar("How Easy Is It To Understand?", main["clarity"])}'
            f'{html_bar("How Clear Is The Benefit?", main["benefit"])}'
            f'{html_bar("How Much Does It Make People Act Now?", main["urgency"])}'
            f'{html_bar("How Easy To Take Action? (lower friction is better)", main["friction"])}'
            '</div>'
        )
        st.markdown(left_card, unsafe_allow_html=True)

    with col2:
        right_card = (
            '<div class="card-box">'
            '<div class="card-title">What We Found — And Why It Matters</div>'
            f'{html_diagnosis_block("Your Headline (First Impression)", main["headline_flaw"], main["headline_lesson"])}'
            '<hr style="border-color:#1F2937; margin:14px 0;">'
            f'{html_diagnosis_block("Your Offer (What They Get)", main["value_flaw"], main["value_lesson"])}'
            '<hr style="border-color:#1F2937; margin:14px 0;">'
            f'{html_diagnosis_block("Your Call-to-Action (The Button)", main["cta_flaw"], main["cta_lesson"])}'
            '</div>'
        )
        st.markdown(right_card, unsafe_allow_html=True)

METRIC_LESSON_MAP = {
    "Message Clarity": "headline_lesson",
    "Benefit Alignment": "value_lesson",
    "CTA Urgency": "cta_lesson",
}
FRICTION_FALLBACK_LESSON = ("Lower friction doesn't mean fewer words — it means the next step is obvious at a "
                             "glance, with nothing making a visitor pause to figure out what to do.")


def render_battle_scorecard(main, comp):
    winner, gap, breakdown = compute_winner(main, comp)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="site-label-blue">YOUR ITEM</span>', unsafe_allow_html=True)
        card_main = (
            '<div class="card-box">'
            f'<div class="score-value">{main["orig_score"]} / 100</div>'
            '<div class="score-sub">Overall Score</div>'
            f'<div class="model-caption">Engine Model: {esc(main["used_model"])}</div>'
            f'{html_bar("How Easy Is It To Understand?", main["clarity"])}'
            f'{html_bar("How Clear Is The Benefit?", main["benefit"])}'
            f'{html_bar("How Much Does It Make People Act Now?", main["urgency"])}'
            f'{html_bar("How Easy To Take Action? (lower friction is better)", main["friction"])}'
            '</div>'
        )
        st.markdown(card_main, unsafe_allow_html=True)

    with col2:
        st.markdown('<span class="site-label-red">COMPETITOR</span>', unsafe_allow_html=True)
        card_comp = (
            '<div class="card-box">'
            f'<div class="score-value">{comp["orig_score"]} / 100</div>'
            '<div class="score-sub">Overall Score</div>'
            f'<div class="model-caption">Engine Model: {esc(comp["used_model"])}</div>'
            f'{html_bar("How Easy Is It To Understand?", comp["clarity"])}'
            f'{html_bar("How Clear Is The Benefit?", comp["benefit"])}'
            f'{html_bar("How Much Does It Make People Act Now?", comp["urgency"])}'
            f'{html_bar("How Easy To Take Action? (lower friction is better)", comp["friction"])}'
            '</div>'
        )
        st.markdown(card_comp, unsafe_allow_html=True)

    if winner == "yours":
        winner_html = f'<span class="winner-badge">🏆 Your site/pitch wins by {gap} points</span>'
    elif winner == "competitor":
        winner_html = f'<span class="loser-badge">⚠️ Competitor leads by {gap} points</span>'
    else:
        winner_html = '<span class="brand-badge">🤝 Dead heat — scores are tied</span>'

    row_parts = []
    for label, m_val, c_val, side_winner, _gap_val in breakdown:
        icon = "🟦" if side_winner == "yours" else ("🟥" if side_winner == "competitor" else "⚪")
        row_parts.append(f'<div class="diagnosis-body">{icon} <b>{esc(label)}</b> — Yours: {m_val} · Competitor: {c_val}</div>')
    rows_html = "".join(row_parts)

    key_lesson_html = ""
    non_tied = [row for row in breakdown if row[3] != "tie"]
    if non_tied:
        biggest_label, biggest_m, biggest_c, biggest_winner, _ = max(non_tied, key=lambda row: row[4])
        source_data = main if biggest_winner == "yours" else comp
        lesson_key = METRIC_LESSON_MAP.get(biggest_label)
        lesson_text = source_data.get(lesson_key, FRICTION_FALLBACK_LESSON) if lesson_key else FRICTION_FALLBACK_LESSON
        key_lesson_html = (
            f'<div class="principle-line">🎓 <b>Key Lesson:</b> the widest gap was in <b>{esc(biggest_label)}</b> — '
            f'{esc(lesson_text)}</div>'
        )

    outcome_card = (
        '<div class="card-box">'
        '<div class="card-title">Competitor Battle Outcome</div>'
        f'{winner_html}'
        f'<div style="margin-top:14px;">{rows_html}</div>'
        f'{key_lesson_html}'
        '</div>'
    )
    st.markdown(outcome_card, unsafe_allow_html=True)

    with st.expander("🔍 Full Diagnosis — Your Site"):
        st.markdown(f"**Your Headline (First Impression):** {main['headline_flaw']}")
        st.caption(f"Why it matters: {main['headline_lesson']}")
        st.markdown(f"**Your Offer (What They Get):** {main['value_flaw']}")
        st.caption(f"Why it matters: {main['value_lesson']}")
        st.markdown(f"**Your Call-to-Action (The Button):** {main['cta_flaw']}")
        st.caption(f"Why it matters: {main['cta_lesson']}")

    with st.expander("🔍 Full Diagnosis — Competitor"):
        st.markdown(f"**Their Headline (First Impression):** {comp['headline_flaw']}")
        st.caption(f"Why it matters: {comp['headline_lesson']}")
        st.markdown(f"**Their Offer (What They Get):** {comp['value_flaw']}")
        st.caption(f"Why it matters: {comp['value_lesson']}")
        st.markdown(f"**Their Call-to-Action (The Button):** {comp['cta_flaw']}")
        st.caption(f"Why it matters: {comp['cta_lesson']}")

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
                st.components.v1.html(render_hero_preview(main, "main"), height=680, scrolling=True)
            with c2:
                st.markdown('<span class="site-label-red">COMPETITOR</span>', unsafe_allow_html=True)
                st.components.v1.html(render_hero_preview(comp, "comp"), height=680, scrolling=True)
        else:
            st.components.v1.html(render_hero_preview(main, "main"), height=680, scrolling=True)

    with tab3:
        st.subheader("Ready-to-Use HTML")
        st.caption("Clean, standalone hero section — production-ready, no app UI baked in.")
        if is_battle and comp:
            sub1, sub2 = st.tabs(["Your Item HTML", "Competitor Item HTML"])
            with sub1:
                html_main = render_export_html(main)
                st.caption("Hero section HTML code for **Your Item**:")
                st.code(html_main, language="html")
                st.download_button("Download Your Item HTML", data=html_main, file_name="your_hero_redesign.html", mime="text/html")
            with sub2:
                html_comp = render_export_html(comp)
                st.caption("Hero section HTML code for **Competitor**:")
                st.code(html_comp, language="html")
                st.download_button("Download Competitor HTML", data=html_comp, file_name="competitor_hero.html", mime="text/html")
        else:
            html_main = render_export_html(main)
            st.code(html_main, language="html")
            st.download_button("Download Hero HTML", data=html_main, file_name="hero_redesign.html", mime="text/html")

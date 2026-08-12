import streamlit as st
from astro_core import compute_moon_position
from gun_milan import compute_ashtakoot
from free_extract import extract_details, extract_text_from_image

st.set_page_config(page_title="Kundli Milan — Free Guna Matching", page_icon="🌙", layout="centered")

# ---------------------------------------------------------------------------
# Theme: midnight-sky indigo + marigold gold. Rooted in the actual subject —
# this whole system is about where the Moon sat in the night sky at birth.
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --ink-950: #14152E;
    --ink-900: #1B1C3D;
    --ink-800: #262852;
    --ink-700: #333667;
    --gold: #E3A94C;
    --gold-soft: #F0C87A;
    --rose: #D9704F;
    --sage: #7FAE8C;
    --ivory: #F4EFE3;
    --ivory-dim: #C9C4D9;
}

.stApp {
    background: linear-gradient(180deg, var(--ink-950) 0%, var(--ink-900) 100%);
    color: var(--ivory);
}
h1, h2, h3 { font-family: 'Fraunces', serif !important; color: var(--ivory) !important; }
p, div, span, label { font-family: 'Inter', sans-serif; }

.hero-title {
    font-family: 'Fraunces', serif;
    font-size: 2.6rem;
    font-weight: 700;
    color: var(--ivory);
    text-align: center;
    margin-bottom: 0.1rem;
    letter-spacing: -0.01em;
}
.hero-sub {
    text-align: center;
    color: var(--ivory-dim);
    font-size: 1.02rem;
    margin-bottom: 2rem;
}

.person-card {
    background: var(--ink-800);
    border: 1px solid var(--ink-700);
    border-radius: 16px;
    padding: 1.4rem 1.3rem 0.6rem 1.3rem;
    margin-bottom: 1rem;
}
.person-label {
    font-family: 'Fraunces', serif;
    font-size: 1.2rem;
    color: var(--gold-soft);
    margin-bottom: 0.6rem;
}

.koota-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.55rem 0.9rem; border-radius: 10px; margin-bottom: 0.4rem;
    background: var(--ink-800); border: 1px solid var(--ink-700);
}
.koota-name { color: var(--ivory); font-weight: 600; font-size: 0.92rem; }
.koota-note { color: var(--ivory-dim); font-size: 0.8rem; }
.koota-score { color: var(--gold-soft); font-weight: 700; font-size: 0.95rem; }

.dosha-badge {
    display: inline-block; padding: 0.35rem 0.9rem; border-radius: 999px;
    font-size: 0.85rem; font-weight: 600; margin: 0.2rem 0.3rem 0.2rem 0;
}
.dosha-bad { background: rgba(217,112,79,0.18); color: var(--rose); border: 1px solid rgba(217,112,79,0.4); }
.dosha-good { background: rgba(127,174,140,0.18); color: var(--sage); border: 1px solid rgba(127,174,140,0.4); }

.verdict-box {
    background: var(--ink-800); border-left: 3px solid var(--gold);
    border-radius: 10px; padding: 1.1rem 1.3rem; margin-top: 1rem;
    color: var(--ivory); line-height: 1.55; font-size: 0.98rem;
}

div[data-testid="stFileUploader"], .stTextArea textarea, .stTextInput input {
    background: var(--ink-950) !important; color: var(--ivory) !important;
    border: 1px solid var(--ink-700) !important; border-radius: 10px !important;
}
.stButton button {
    background: var(--gold) !important; color: var(--ink-950) !important;
    font-weight: 700 !important; border-radius: 10px !important; border: none !important;
}
.stButton button:hover { background: var(--gold-soft) !important; }
hr { border-color: var(--ink-700) !important; }
</style>
""", unsafe_allow_html=True)


def score_ring_svg(score: float, max_score: int = 36) -> str:
    """Signature element: a radial dial showing the guna score, gold arc on indigo."""
    pct = max(0, min(1, score / max_score))
    radius, stroke = 70, 14
    circumference = 2 * 3.14159265 * radius
    offset = circumference * (1 - pct)
    color = "#7FAE8C" if score >= 18 else "#D9704F"
    return f"""
    <div style="display:flex; justify-content:center; margin: 1.2rem 0;">
      <svg width="200" height="200" viewBox="0 0 200 200">
        <circle cx="100" cy="100" r="{radius}" fill="none" stroke="#333667" stroke-width="{stroke}"/>
        <circle cx="100" cy="100" r="{radius}" fill="none" stroke="{color}" stroke-width="{stroke}"
                stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
                stroke-linecap="round" transform="rotate(-90 100 100)"/>
        <text x="100" y="94" text-anchor="middle" font-family="Fraunces, serif" font-size="34"
              font-weight="700" fill="#F4EFE3">{score:g}</text>
        <text x="100" y="118" text-anchor="middle" font-family="Inter, sans-serif" font-size="13"
              fill="#C9C4D9">out of {max_score}</text>
      </svg>
    </div>
    """


def build_verdict(result: dict) -> str:
    """Rule-based plain-English summary — no API call, fully free."""
    score = result["total_score"]
    lines = []
    if score >= 32:
        lines.append("This is an excellent Guna Milan score — the kind considered rare and highly favourable.")
    elif score >= 24:
        lines.append("This is a strong score, generally considered very good for marriage compatibility.")
    elif score >= 18:
        lines.append("This score clears the traditional minimum of 18 points, generally considered an acceptable match.")
    else:
        lines.append("This score falls below the traditional 18-point minimum, which is generally considered weak on paper.")

    if result["nadi_dosha"]:
        lines.append("Both partners share the same Nadi, which classically carries the most weight of any single "
                      "factor and is traditionally linked to health and progeny concerns — most families would want "
                      "an astrologer's view on possible remedies (Nadi Dosha Pariharas) before proceeding.")
    if result["bhakoot_dosha"]:
        lines.append("The Moon signs fall in a classically inauspicious distance from each other (Bhakoot Dosha), "
                      "traditionally associated with friction in shared finances or family life.")
    if not result["nadi_dosha"] and not result["bhakoot_dosha"]:
        lines.append("Neither of the two heavyweight doshas (Nadi or Bhakoot) is present, which is a reassuring sign "
                      "even where the total score isn't very high.")

    lines.append("As with any Kundli Milan tool, treat this as a starting point — a professional astrologer "
                  "weighs additional charts and context beyond this 36-point score.")
    return " ".join(lines)


def person_input(label: str, key_prefix: str):
    st.markdown(f'<div class="person-card"><div class="person-label">{label}</div>', unsafe_allow_html=True)
    mode = st.radio("Input method", ["Paste text", "Upload screenshot"], key=f"{key_prefix}_mode", horizontal=True, label_visibility="collapsed")

    if mode == "Paste text":
        raw = st.text_area("Paste details", key=f"{key_prefix}_text", height=90,
                            placeholder="e.g. Name: Ritik Sharma, DOB: 15 Aug 1995, Time: 2:30 PM, Place: Delhi",
                            label_visibility="collapsed")
        if raw and st.button(f"Extract", key=f"{key_prefix}_extract_btn"):
            st.session_state[f"{key_prefix}_details"] = extract_details(raw)
    else:
        uploaded = st.file_uploader("Upload screenshot", type=["png", "jpg", "jpeg"], key=f"{key_prefix}_upload", label_visibility="collapsed")
        if uploaded and st.button(f"Extract", key=f"{key_prefix}_extract_btn"):
            with st.spinner("Reading screenshot..."):
                ocr_text = extract_text_from_image(uploaded.read())
                st.session_state[f"{key_prefix}_details"] = extract_details(ocr_text)

    stored = st.session_state.get(f"{key_prefix}_details", {})
    name = st.text_input("Name", value=stored.get("name") or "", key=f"{key_prefix}_name")
    dob = st.text_input("Date of birth (YYYY-MM-DD)", value=stored.get("dob") or "", key=f"{key_prefix}_dob")
    tob = st.text_input("Time of birth (HH:MM, 24hr)", value=stored.get("tob") or "", key=f"{key_prefix}_tob")
    place = st.text_input("Place of birth", value=stored.get("place") or "", key=f"{key_prefix}_place")
    st.markdown('</div>', unsafe_allow_html=True)
    return {"name": name, "dob": dob, "tob": tob, "place": place}


st.markdown('<div class="hero-title">🌙 Kundli Milan</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Free Guna Milan matching — paste details or upload a screenshot for both</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    boy = person_input("Boy", "boy")
with col2:
    girl = person_input("Girl", "girl")

st.write("")
match_clicked = st.button("Match Kundli", type="primary", use_container_width=True)

if match_clicked:
    if not (boy["dob"] and boy["tob"] and boy["place"]):
        st.error("Boy's date of birth, time of birth and place are required.")
    elif not (girl["dob"] and girl["tob"] and girl["place"]):
        st.error("Girl's date of birth, time of birth and place are required.")
    else:
        with st.spinner("Calculating planetary positions..."):
            try:
                boy_moon = compute_moon_position(boy["dob"], boy["tob"], boy["place"])
                girl_moon = compute_moon_position(girl["dob"], girl["tob"], girl["place"])
                result = compute_ashtakoot(boy_moon, girl_moon)

                st.markdown(score_ring_svg(result["total_score"], result["max_score"]), unsafe_allow_html=True)

                badges = ""
                badges += '<span class="dosha-badge dosha-bad">⚠ Nadi Dosha</span>' if result["nadi_dosha"] else '<span class="dosha-badge dosha-good">✓ No Nadi Dosha</span>'
                badges += '<span class="dosha-badge dosha-bad">⚠ Bhakoot Dosha</span>' if result["bhakoot_dosha"] else '<span class="dosha-badge dosha-good">✓ No Bhakoot Dosha</span>'
                st.markdown(f'<div style="text-align:center; margin-bottom:1rem;">{badges}</div>', unsafe_allow_html=True)

                for name, (score, maxs, note) in result["kootas"].items():
                    st.markdown(f"""
                    <div class="koota-row">
                        <div><span class="koota-name">{name}</span><br><span class="koota-note">{note}</span></div>
                        <div class="koota-score">{score:g}/{maxs}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown(f'<div class="verdict-box">{build_verdict(result)}</div>', unsafe_allow_html=True)

            except ValueError as e:
                st.error(str(e))

st.markdown("<br>", unsafe_allow_html=True)
st.caption("Free build for testing. Extraction uses OCR/pattern-matching — double-check the auto-filled fields "
           "before matching. Ashtakoot rules follow standard Lahiri-ayanamsa conventions; for real decisions, "
           "cross-check with a professional astrologer.")

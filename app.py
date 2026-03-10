import os
import streamlit as st
from dotenv import load_dotenv

from utils.pdf_extractor import extract_screenplay_text, get_screenplay_preview
from utils.coverage_generator import generate_coverage


# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Script Coverage AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── API key ────────────────────────────────────────────────────────────────────
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except (KeyError, FileNotFoundError):
        pass

# ── Session state defaults ─────────────────────────────────────────────────────
for _k, _v in [
    ("coverage", None),
    ("screenplay_text", None),
    ("metadata", None),
    ("file_key", None),
    ("filename", None),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        .stApp { background-color: #0d0d0d; color: #e8e8e8; }

        [data-testid="stSidebar"] {
            background-color: #141414;
            border-right: 1px solid #2a2a2a;
        }
        h1, h2, h3 { color: #c9a84c !important; }
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] li { color: #b0b0b0; }

        [data-testid="stFileUploader"] {
            background-color: #1a1a1a;
            border: 1px dashed #c9a84c;
            border-radius: 8px;
            padding: 1rem;
        }

        .stButton > button {
            background-color: #c9a84c;
            color: #0d0d0d;
            font-weight: 700;
            border: none;
            border-radius: 6px;
            padding: 0.6rem 2rem;
            font-size: 1rem;
            letter-spacing: 0.05em;
            transition: background-color 0.2s ease;
        }
        .stButton > button:hover { background-color: #e0be6a; color: #0d0d0d; }
        .stButton > button:disabled { background-color: #3a3a2a; color: #666; }

        [data-testid="stDownloadButton"] > button {
            background-color: #1a1a1a;
            color: #c9a84c;
            border: 1px solid #c9a84c;
            border-radius: 6px;
            font-weight: 600;
            padding: 0.5rem 1.5rem;
        }
        [data-testid="stDownloadButton"] > button:hover { background-color: #252510; }

        hr { border-color: #2a2a2a; }

        .placeholder-box {
            background-color: #1a1a1a;
            border: 1px solid #2a2a2a;
            border-left: 4px solid #c9a84c;
            border-radius: 6px;
            padding: 1.5rem 2rem;
            color: #888;
            font-size: 0.95rem;
            margin-top: 1.5rem;
        }

        /* ── Coverage report components ── */

        .rec-badge {
            display: inline-block;
            padding: 0.5rem 2rem;
            border-radius: 6px;
            font-size: 1.4rem;
            font-weight: 800;
            letter-spacing: 0.15em;
        }
        .rec-recommend { background-color: #0f2d0f; color: #4ade80; border: 1px solid #4ade80; }
        .rec-consider  { background-color: #2d2200; color: #fbbf24; border: 1px solid #fbbf24; }
        .rec-pass      { background-color: #2d0f0f; color: #f87171; border: 1px solid #f87171; }

        .logline-box {
            background-color: #1a1a0a;
            border-left: 4px solid #c9a84c;
            border-radius: 0 6px 6px 0;
            padding: 1rem 1.5rem;
            color: #e8e8d0;
            font-style: italic;
            font-size: 1.05rem;
            line-height: 1.7;
            margin-bottom: 0.5rem;
        }

        .section-header {
            color: #c9a84c;
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            border-bottom: 1px solid #2a2a2a;
            padding-bottom: 0.3rem;
            margin: 1.5rem 0 0.75rem 0;
        }

        .theme-tag {
            display: inline-block;
            background-color: #1e1a08;
            color: #c9a84c;
            border: 1px solid #4a3c10;
            border-radius: 20px;
            padding: 0.25rem 0.9rem;
            margin: 0.2rem 0.2rem;
            font-size: 0.85rem;
        }

        .comp-title {
            background-color: #111128;
            border: 1px solid #2a2a4a;
            border-radius: 6px;
            padding: 0.6rem 1rem;
            color: #a0a0d8;
            font-size: 0.9rem;
            text-align: center;
            margin: 0.25rem 0;
        }

        .strength-item { color: #4ade80; padding: 0.3rem 0; }
        .weakness-item { color: #f87171; padding: 0.3rem 0; }

        .callout-box {
            background-color: #0d1520;
            border: 1px solid #1e3a5f;
            border-left: 4px solid #3b82f6;
            border-radius: 0 6px 6px 0;
            padding: 1rem 1.5rem;
            color: #93c5fd;
            font-size: 0.95rem;
            line-height: 1.7;
        }

        /* ── Footer ── */
        .footer {
            position: fixed;
            bottom: 0; left: 0; right: 0;
            background-color: #0d0d0d;
            border-top: 1px solid #1e1e1e;
            padding: 0.55rem 2rem;
            text-align: center;
            color: #4a4a4a;
            font-size: 0.78rem;
            z-index: 1000;
        }
        .footer a { color: #c9a84c; text-decoration: none; }
        .footer a:hover { text-decoration: underline; }

        /* Push content above fixed footer */
        .stApp { padding-bottom: 3.5rem; }

        /* Sidebar sample coverage card */
        .sample-card {
            background-color: #0d0d0d;
            border: 1px solid #2a2a2a;
            border-radius: 6px;
            padding: 0.75rem 0.9rem;
            font-size: 0.83rem;
            line-height: 1.55;
            color: #b0b0b0;
        }
        .sample-card strong { color: #e8e8e8; }
        .sample-logline {
            color: #c8c8b0;
            font-style: italic;
            margin: 0.4rem 0;
        }
        .sample-str { color: #4ade80; }
        .sample-wk  { color: #f87171; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎬 Script Coverage AI")
    st.markdown("---")
    st.markdown(
        "**Script Coverage AI** transforms your screenplay PDF into a "
        "professional industry-standard coverage report in seconds, powered "
        "by Claude AI."
    )
    st.markdown("---")
    st.markdown("### How it works")
    st.markdown(
        """
        1. **Upload** your screenplay as a PDF
        2. Click **Generate Coverage**
        3. Receive a full coverage report including:
           - Logline & synopsis
           - Character analysis
           - Themes & comparable titles
           - Strengths & weaknesses
           - Recommendation with score
        """
    )
    st.markdown("---")
    st.markdown("### Sample Coverage")
    with st.expander("View — *Casablanca* (1942)"):
        st.markdown(
            '<span class="rec-badge rec-recommend" '
            'style="font-size:0.85rem;padding:0.3rem 1rem">RECOMMEND</span>'
            "&nbsp;&nbsp;<strong style='color:#e8e8e8'>9 / 10</strong>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="sample-card" style="margin-top:0.6rem">'
            "<strong>Feature</strong> · Romantic Drama / War Thriller<br><br>"
            '<span class="sample-logline">'
            "A cynical American café owner in wartime Casablanca must choose between "
            "self-preservation and helping his former lover and her Resistance leader "
            "husband escape the Nazis — sacrificing the only thing he has left to lose."
            "</span><br><br>"
            "<strong>Themes:</strong><br>"
            '<span class="theme-tag" style="font-size:0.75rem">Sacrifice</span>'
            '<span class="theme-tag" style="font-size:0.75rem">Redemption</span>'
            '<span class="theme-tag" style="font-size:0.75rem">Love &amp; Duty</span>'
            '<span class="theme-tag" style="font-size:0.75rem">Moral Ambiguity</span>'
            "<br><br>"
            "<strong>Strengths:</strong><br>"
            '<div class="sample-str">✓ Razor-sharp, iconic dialogue</div>'
            '<div class="sample-str">✓ Flawless three-act structure</div>'
            '<div class="sample-str">✓ Morally complex protagonist arc</div>'
            "<br><strong>Weaknesses:</strong><br>"
            '<div class="sample-wk">✗ Secondary characters thinly drawn</div>'
            '<div class="sample-wk">✗ Third-act convenience strains credulity</div>'
            "</div>",
            unsafe_allow_html=True,
        )
        st.caption("Sample output for illustration purposes only.")
    st.markdown("---")
    st.caption("Built for the entertainment industry · Powered by Claude AI")


# ── Render helpers ─────────────────────────────────────────────────────────────

def _rec_badge_html(rec: str) -> str:
    css = {
        "RECOMMEND": "rec-recommend",
        "CONSIDER":  "rec-consider",
        "PASS":      "rec-pass",
    }.get(rec.upper().strip(), "rec-consider")
    return f'<span class="rec-badge {css}">{rec.upper()}</span>'


def _render_coverage(coverage: dict, filename: str) -> None:
    st.markdown("---")
    st.markdown("## Coverage Report")

    # 1. Title / format / genre header
    st.markdown(f"### {coverage.get('title', 'Untitled')}")
    fmt     = coverage.get("format", "—")
    genre   = coverage.get("genre", "—")
    sub     = coverage.get("subgenre", "—")
    st.markdown(
        f"**Format:** {fmt} &nbsp;·&nbsp; **Genre:** {genre} &nbsp;·&nbsp; **Subgenre:** {sub}"
    )

    # 2. Recommendation badge + score + rationale
    rec   = coverage.get("recommendation", "N/A")
    score = coverage.get("overall_score", "—")
    col_rec, col_score, col_reason = st.columns([2, 1, 4])
    with col_rec:
        st.markdown(_rec_badge_html(rec), unsafe_allow_html=True)
    with col_score:
        st.metric("Score", f"{score} / 10")
    with col_reason:
        st.markdown(f"_{coverage.get('recommendation_reason', '')}_")

    # 3. Logline
    st.markdown('<div class="section-header">Logline</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="logline-box">{coverage.get("logline", "—")}</div>',
        unsafe_allow_html=True,
    )

    # 4. Synopsis
    st.markdown('<div class="section-header">Synopsis</div>', unsafe_allow_html=True)
    st.markdown(coverage.get("synopsis", "—"))

    # 5. Tone + Setting
    col_tone, col_set = st.columns(2)
    with col_tone:
        st.markdown('<div class="section-header">Tone</div>', unsafe_allow_html=True)
        st.markdown(coverage.get("tone", "—"))
    with col_set:
        st.markdown('<div class="section-header">Setting</div>', unsafe_allow_html=True)
        st.markdown(coverage.get("setting", "—"))

    # 6. Protagonist
    prot = coverage.get("protagonist", {})
    if prot:
        st.markdown('<div class="section-header">Protagonist</div>', unsafe_allow_html=True)
        st.markdown(f"**{prot.get('name', '—')}** — {prot.get('description', '')}")
        st.markdown(f"*Arc: {prot.get('arc', '—')}*")

    # 7. Supporting characters
    supporting = coverage.get("supporting_characters", [])
    if supporting:
        st.markdown('<div class="section-header">Supporting Characters</div>', unsafe_allow_html=True)
        for char in supporting:
            st.markdown(f"- **{char.get('name', '—')}** — {char.get('role', '')}")

    # 8. Themes as badge tags
    themes = coverage.get("themes", [])
    if themes:
        st.markdown('<div class="section-header">Themes</div>', unsafe_allow_html=True)
        tags_html = "".join(f'<span class="theme-tag">{t}</span>' for t in themes)
        st.markdown(f'<div style="margin-top:0.4rem">{tags_html}</div>', unsafe_allow_html=True)

    # 9. Comparable titles
    comp = coverage.get("comparable_titles", [])
    if comp:
        st.markdown('<div class="section-header">Comparable Titles</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(comp), 4))
        for col, title in zip(cols, comp[:4]):
            with col:
                st.markdown(
                    f'<div class="comp-title">🎬 {title}</div>',
                    unsafe_allow_html=True,
                )

    # 10. Strengths (green) + Weaknesses (red)
    col_s, col_w = st.columns(2)
    with col_s:
        st.markdown('<div class="section-header">Strengths</div>', unsafe_allow_html=True)
        for item in coverage.get("strengths", []):
            st.markdown(
                f'<div class="strength-item">✓ &nbsp;{item}</div>',
                unsafe_allow_html=True,
            )
    with col_w:
        st.markdown('<div class="section-header">Weaknesses</div>', unsafe_allow_html=True)
        for item in coverage.get("weaknesses", []):
            st.markdown(
                f'<div class="weakness-item">✗ &nbsp;{item}</div>',
                unsafe_allow_html=True,
            )

    # 11. Marketability
    st.markdown('<div class="section-header">Marketability</div>', unsafe_allow_html=True)
    st.markdown(coverage.get("marketability", "—"))

    # 12. Analyst notes callout
    notes = coverage.get("analyst_notes", "")
    if notes:
        st.markdown('<div class="section-header">Analyst Notes</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="callout-box">{notes}</div>',
            unsafe_allow_html=True,
        )

    # 13. Download button
    st.markdown("---")
    dl_text   = _build_download_text(coverage, filename)
    safe_name = os.path.splitext(filename)[0].replace(" ", "_")
    st.download_button(
        label="⬇  Download Coverage Report",
        data=dl_text,
        file_name=f"{safe_name}_coverage.txt",
        mime="text/plain",
    )


def _build_download_text(coverage: dict, filename: str) -> str:
    """Format the coverage dict as a readable plain-text file."""
    SEP  = "=" * 70
    DASH = "-" * 70

    def section(title: str, body: str) -> str:
        return f"{title}\n{DASH}\n{body}\n\n"

    lines = [
        SEP,
        "SCRIPT COVERAGE REPORT",
        "Generated by Script Coverage AI  ·  Powered by Claude AI",
        SEP,
        "",
        f"TITLE:       {coverage.get('title', 'N/A')}",
        f"FORMAT:      {coverage.get('format', 'N/A')}",
        f"GENRE:       {coverage.get('genre', 'N/A')}",
        f"SUBGENRE:    {coverage.get('subgenre', 'N/A')}",
        f"SETTING:     {coverage.get('setting', 'N/A')}",
        f"TONE:        {coverage.get('tone', 'N/A')}",
        "",
        f"RECOMMENDATION:  {coverage.get('recommendation', 'N/A')}",
        f"OVERALL SCORE:   {coverage.get('overall_score', 'N/A')} / 10",
        "",
    ]

    lines.append(section("LOGLINE", coverage.get("logline", "N/A")))
    lines.append(section("SYNOPSIS", coverage.get("synopsis", "N/A")))

    prot = coverage.get("protagonist", {})
    lines.append(section(
        "PROTAGONIST",
        f"Name:        {prot.get('name', 'N/A')}\n"
        f"Description: {prot.get('description', 'N/A')}\n"
        f"Arc:         {prot.get('arc', 'N/A')}",
    ))

    sup = "\n".join(
        f"• {c.get('name', '')}: {c.get('role', '')}"
        for c in coverage.get("supporting_characters", [])
    ) or "N/A"
    lines.append(section("SUPPORTING CHARACTERS", sup))

    themes_str = "\n".join(f"• {t}" for t in coverage.get("themes", [])) or "N/A"
    lines.append(section("THEMES", themes_str))

    comp_str = "\n".join(f"• {t}" for t in coverage.get("comparable_titles", [])) or "N/A"
    lines.append(section("COMPARABLE TITLES", comp_str))

    str_str = "\n".join(f"✓ {s}" for s in coverage.get("strengths", [])) or "N/A"
    lines.append(section("STRENGTHS", str_str))

    weak_str = "\n".join(f"✗ {w}" for w in coverage.get("weaknesses", [])) or "N/A"
    lines.append(section("WEAKNESSES", weak_str))

    lines.append(section("MARKETABILITY", coverage.get("marketability", "N/A")))
    lines.append(section("RECOMMENDATION RATIONALE", coverage.get("recommendation_reason", "N/A")))
    lines.append(section("ANALYST NOTES", coverage.get("analyst_notes", "N/A")))

    lines += [SEP, f"Source file: {filename}", SEP]
    return "\n".join(lines)


# ── Main area ──────────────────────────────────────────────────────────────────
st.title("Script Coverage AI")
st.markdown("Upload a screenplay PDF and generate professional script coverage instantly.")
st.markdown("---")

if not api_key:
    st.warning(
        "**No API key detected.** Add `ANTHROPIC_API_KEY` to your `.env` file "
        "or Streamlit secrets to enable coverage generation."
    )

uploaded_file = st.file_uploader(
    "Drop your screenplay here",
    type=["pdf"],
    help="Accepts standard screenplay PDFs. Maximum recommended length: 200 pages.",
)

# ── File uploaded ──────────────────────────────────────────────────────────────
if uploaded_file:
    file_key = f"{uploaded_file.name}_{uploaded_file.size}"

    # Extract only when a new/different file is detected
    if file_key != st.session_state.file_key:
        with st.spinner("Reading PDF…"):
            text, metadata = extract_screenplay_text(uploaded_file)
        if text and metadata:
            st.session_state.screenplay_text = text
            st.session_state.metadata        = metadata
            st.session_state.file_key        = file_key
            st.session_state.filename        = uploaded_file.name
            st.session_state.coverage        = None   # reset for new file
        else:
            st.error(
                "**Could not read this PDF.** The file may be corrupted, password-protected, "
                "or in an unsupported format.\n\n"
                "Please try re-exporting the PDF from your screenwriting software and uploading again."
            )
            st.stop()

    # Metadata row
    meta = st.session_state.metadata
    if meta:
        c1, c2, _ = st.columns([1, 1, 5])
        c1.metric("Pages", meta["page_count"])
        c2.metric("Words", f"{meta['word_count']:,}")

    # ── Input validation ──────────────────────────────────────────────────────
    if meta and meta["page_count"] > 500:
        st.warning(
            f"**Long screenplay detected** — This file is {meta['page_count']} pages. "
            "Coverage generation will work but may take longer than usual and consume "
            "more API tokens. For best results, consider uploading a version under 200 pages."
        )

    if st.session_state.screenplay_text and len(st.session_state.screenplay_text) < 1000:
        st.error(
            "**This PDF doesn't contain readable text.** It appears to be a scanned "
            "or image-based document. Script Coverage AI requires a text-based PDF.\n\n"
            "**To fix this:** Export your screenplay directly from your screenwriting "
            "software (Final Draft, Highland, WriterDuet, Fade In) as a PDF, rather "
            "than scanning a printed copy."
        )
        st.stop()

    # Collapsible preview
    if st.session_state.screenplay_text:
        with st.expander("Preview first 20 lines"):
            preview = get_screenplay_preview(st.session_state.screenplay_text)
            st.code(preview, language=None)

    st.markdown("---")

    # Generate button
    col_btn, _ = st.columns([2, 5])
    with col_btn:
        generate_btn = st.button(
            "Generate Coverage",
            disabled=not bool(api_key),
            use_container_width=True,
        )

    if generate_btn:
        with st.spinner("Reading screenplay… generating coverage report…"):
            result = generate_coverage(st.session_state.screenplay_text, api_key)
        st.session_state.coverage = result

    # Render persisted coverage
    if st.session_state.coverage:
        if "_error" in st.session_state.coverage:
            err = st.session_state.coverage["_error"]
            if "Invalid API key" in err:
                st.error(
                    "**Authentication failed.** Your API key appears to be invalid or expired.\n\n"
                    "Check that `ANTHROPIC_API_KEY` in your `.env` file is correct and hasn't been revoked."
                )
            elif "Rate limit" in err:
                st.error(
                    "**Rate limit reached.** The API is temporarily throttling requests.\n\n"
                    "Please wait 30–60 seconds and click **Generate Coverage** again."
                )
            elif "API error" in err:
                st.error(
                    f"**The coverage service returned an error.** {err}\n\n"
                    "This is usually temporary — please try again in a moment."
                )
            else:
                st.error(
                    f"**Coverage generation failed.** {err}\n\n"
                    "If this keeps happening, check your API key and internet connection."
                )
            if "_raw" in st.session_state.coverage:
                with st.expander("Show raw model output"):
                    st.text(st.session_state.coverage["_raw"])
        else:
            _render_coverage(
                st.session_state.coverage,
                st.session_state.filename or uploaded_file.name,
            )

# ── No file placeholder ────────────────────────────────────────────────────────
else:
    st.markdown(
        """
        <div class="placeholder-box">
            📄 &nbsp; No screenplay uploaded yet. Upload a PDF above to get started.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Footer (always visible) ────────────────────────────────────────────────────
st.markdown(
    """
    <div class="footer">
        Built by
        <a href="https://www.linkedin.com/in/sunilsukumar" target="_blank" rel="noopener">
            Sunil Sukumar
        </a>
        &nbsp;|&nbsp; AI Product Portfolio
    </div>
    """,
    unsafe_allow_html=True,
)

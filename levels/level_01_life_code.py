"""
FAZENIUM — Level 1: Life Code
Interactive FASTA/FASTQ parser sandbox
"""
import json
import os
import streamlit as st
from modules.localization import t
from modules.ui_components import (
    render_section_divider, colorize_sequence, render_gemma_message, render_metric_card
)
from modules.gemma_engine import get_gemma_engine
from config import DATA_DIR


def _load_threats():
    path = os.path.join(DATA_DIR, "threats.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _parse_fasta(text: str):
    """Parse FASTA format text, return list of (header, sequence) tuples."""
    records = []
    header, seq_lines = None, []
    for line in text.strip().splitlines():
        line = line.strip()
        if line.startswith(">"):
            if header is not None:
                records.append((header, "".join(seq_lines)))
            header = line[1:].strip()
            seq_lines = []
        elif header is not None:
            seq_lines.append(line.replace(" ", ""))
    if header is not None:
        records.append((header, "".join(seq_lines)))
    return records


def _parse_fastq(text: str):
    """Parse FASTQ format text, return list of (header, sequence, quality) tuples."""
    records = []
    lines = text.strip().splitlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith("@"):
            header = lines[i][1:].strip()
            seq = lines[i + 1].strip() if i + 1 < len(lines) else ""
            qual = lines[i + 3].strip() if i + 3 < len(lines) else ""
            records.append((header, seq, qual))
            i += 4
        else:
            i += 1
    return records


def _detect_type(seq: str) -> str:
    upper = seq.upper()
    bases = set(upper)
    if bases <= set("ATGCN"):
        return "DNA"
    if bases <= set("AUGCN"):
        return "RNA"
    return "Protein"


def _gc_content(seq: str) -> float:
    upper = seq.upper()
    gc = sum(1 for c in upper if c in "GC")
    total = sum(1 for c in upper if c in "ATUGC")
    return (gc / total * 100) if total > 0 else 0.0


def _render_quality_bar(qual_str: str):
    """Render a quality score visualization for FASTQ."""
    scores = [ord(c) - 33 for c in qual_str]
    if not scores:
        return

    avg = sum(scores) / len(scores)
    max_q = max(scores)
    min_q = min(scores)

    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Avg Quality", f"{avg:.1f}", "📊")
    with c2:
        render_metric_card("Min Quality", str(min_q), "⬇️")
    with c3:
        render_metric_card("Max Quality", str(max_q), "⬆️")


def _analyze_and_display(header: str, seq: str, quality: str = None):
    """Display analysis results for a single sequence."""
    seq_type = _detect_type(seq)
    gc = _gc_content(seq)

    type_key = f"l1_{seq_type.lower()}"

    # Metrics row
    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card(t("l1_length"), f"{len(seq)} bp", "📏")
    with c2:
        render_metric_card(t("l1_gc_content"), f"{gc:.1f}%", "🧬")
    with c3:
        render_metric_card(t("l1_type"), t(type_key), "🔬")

    st.markdown("---")

    # Colored sequence
    st.markdown(f"**{header}**")
    colored = colorize_sequence(seq)
    st.markdown(f"<div class='sequence-display'>{colored}</div>", unsafe_allow_html=True)

    # Quality scores if FASTQ
    if quality:
        st.markdown("---")
        st.markdown("**Quality Scores (Phred+33)**")
        _render_quality_bar(quality)

    # Gemma analysis
    render_section_divider()
    st.markdown(f"<h3>🤖 Gemma Analysis</h3>", unsafe_allow_html=True)

    engine = get_gemma_engine()
    lang = st.session_state.get("language", "en")
    diff = st.session_state.get("difficulty", "student")

    stats = {"length": len(seq), "gc_content": f"{gc:.1f}%", "type": seq_type}
    analysis = engine.get_sequence_analysis(seq_type, seq[:100], stats, diff, lang)
    render_gemma_message(analysis)

    # Award points
    if f"l1_analyzed_{header}" not in st.session_state:
        st.session_state[f"l1_analyzed_{header}"] = True
        st.session_state["fazena_points"] = st.session_state.get("fazena_points", 0) + 25
        st.toast("🧬 +25 FP for sequence analysis!", icon="⚡")


def render_level():
    """Render Level 1: Life Code."""
    st.markdown(f"<h1>🧬 {t('level_1_title')}</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color: var(--fz-text-muted); font-size: 1rem; margin-bottom: 2rem;'>"
        f"{t('level_1_desc')}</p>",
        unsafe_allow_html=True
    )

    # Three sandbox paths
    tab1, tab2, tab3 = st.tabs([
        f"📋 {t('l1_paste')}",
        f"📁 {t('l1_upload')}",
        f"🦠 {t('l1_library')}"
    ])

    with tab1:
        text_input = st.text_area(
            t("l1_paste_hint"),
            height=200,
            placeholder=">Example_Sequence\nATGCCGTAACGTTGA...",
            key="l1_paste_input"
        )
        if st.button(t("l1_analyze"), key="l1_analyze_paste"):
            if text_input.strip():
                # Detect format
                if text_input.strip().startswith("@"):
                    records = _parse_fastq(text_input)
                    for header, seq, qual in records:
                        _analyze_and_display(header, seq, qual)
                else:
                    if not text_input.strip().startswith(">"):
                        text_input = f">User_Sequence\n{text_input.strip()}"
                    records = _parse_fasta(text_input)
                    for header, seq in records:
                        _analyze_and_display(header, seq)

    with tab2:
        uploaded = st.file_uploader(
            t("l1_upload"),
            type=["fasta", "fa", "fna", "fastq", "fq", "txt"],
            key="l1_file_upload"
        )
        if uploaded is not None:
            content = uploaded.read().decode("utf-8", errors="replace")
            if uploaded.name.endswith((".fastq", ".fq")):
                records = _parse_fastq(content)
                for header, seq, qual in records:
                    _analyze_and_display(header, seq, qual)
            else:
                records = _parse_fasta(content)
                for header, seq in records:
                    _analyze_and_display(header, seq)

    with tab3:
        threats = _load_threats()
        lang = st.session_state.get("language", "en")

        cols = st.columns(3)
        for i, threat in enumerate(threats):
            with cols[i % 3]:
                name = threat["name"].get(lang, threat["name"]["en"])
                desc = threat["description"].get(lang, threat["description"]["en"])

                st.markdown(f"""
                <div class="fazena-card" style="cursor: pointer; min-height: 120px;">
                    <div style="font-family: var(--fz-font-heading); font-size: 0.85rem;
                         color: var(--fz-accent); letter-spacing: 1px; text-transform: uppercase;
                         margin-bottom: 0.3rem;">{name}</div>
                    <div style="font-size: 0.78rem; color: var(--fz-text-muted);
                         line-height: 1.5;">{desc}</div>
                    <div style="font-family: var(--fz-font-mono); font-size: 0.65rem;
                         color: var(--fz-text-dim); margin-top: 0.5rem;">
                        {threat['organism']} · {threat['type']} · {len(threat['sequence'])} bp
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"Analyze {threat['id']}", key=f"l1_threat_{threat['id']}"):
                    _analyze_and_display(name, threat["sequence"])

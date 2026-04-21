"""
FAZENIUM — Level 2: Molecular Origami
RNA secondary structure sandbox (Nussinov-based)
"""
import streamlit as st
from modules.localization import t
from modules.ui_components import render_section_divider, render_gemma_message, render_metric_card
from modules.gemma_engine import get_gemma_engine


def _nussinov_fold(seq: str, min_loop: int = 3) -> str:
    """Simplified Nussinov algorithm for RNA secondary structure prediction.
    Returns dot-bracket notation."""
    n = len(seq)
    seq = seq.upper().replace("T", "U")
    pairs = {("A", "U"), ("U", "A"), ("G", "C"), ("C", "G"), ("G", "U"), ("U", "G")}

    # DP table
    dp = [[0] * n for _ in range(n)]

    for length in range(2, n):
        for i in range(n - length):
            j = i + length

            # Case 1: i unpaired
            dp[i][j] = dp[i + 1][j]

            # Case 2: j unpaired
            dp[i][j] = max(dp[i][j], dp[i][j - 1])

            # Case 3: i-j paired
            if (seq[i], seq[j]) in pairs and j - i > min_loop:
                dp[i][j] = max(dp[i][j], dp[i + 1][j - 1] + 1)

            # Case 4: bifurcation
            for k in range(i + 1, j):
                dp[i][j] = max(dp[i][j], dp[i][k] + dp[k + 1][j])

    # Traceback
    structure = ["."] * n

    def traceback(i, j):
        if i >= j:
            return
        if dp[i][j] == dp[i + 1][j]:
            traceback(i + 1, j)
        elif dp[i][j] == dp[i][j - 1]:
            traceback(i, j - 1)
        elif (seq[i], seq[j]) in pairs and j - i > min_loop and dp[i][j] == dp[i + 1][j - 1] + 1:
            structure[i] = "("
            structure[j] = ")"
            traceback(i + 1, j - 1)
        else:
            for k in range(i + 1, j):
                if dp[i][j] == dp[i][k] + dp[k + 1][j]:
                    traceback(i, k)
                    traceback(k + 1, j)
                    break

    traceback(0, n - 1)
    return "".join(structure)


def _count_pairs(bracket: str) -> int:
    return bracket.count("(")


def _approx_energy(num_pairs: int) -> float:
    """Very rough approximation: ~-1.5 kcal/mol per base pair."""
    return -1.5 * num_pairs


def _render_structure_visual(seq: str, bracket: str):
    """Render a colorful dot-bracket visualization."""
    seq_html = []
    for ch, br in zip(seq.upper(), bracket):
        if br == "(":
            color = "var(--fz-accent)"
            weight = "bold"
        elif br == ")":
            color = "var(--fz-accent-alt)"
            weight = "bold"
        else:
            color = "var(--fz-text-dim)"
            weight = "normal"
        seq_html.append(f"<span style='color: {color}; font-weight: {weight};'>{ch}</span>")

    bracket_html = []
    for br in bracket:
        if br == "(":
            bracket_html.append(f"<span style='color: var(--fz-accent);'>{br}</span>")
        elif br == ")":
            bracket_html.append(f"<span style='color: var(--fz-accent-alt);'>{br}</span>")
        else:
            bracket_html.append(f"<span style='color: var(--fz-text-dim);'>{br}</span>")

    st.markdown(f"""
    <div class="sequence-display">
        <div style="margin-bottom: 4px;">{''.join(seq_html)}</div>
        <div>{''.join(bracket_html)}</div>
    </div>
    """, unsafe_allow_html=True)


def _render_arc_diagram(seq: str, bracket: str):
    """Render an SVG arc diagram for base pairs."""
    n = len(seq)
    if n == 0:
        return

    # Find pairs
    stack = []
    pair_list = []
    for i, ch in enumerate(bracket):
        if ch == "(":
            stack.append(i)
        elif ch == ")" and stack:
            j = stack.pop()
            pair_list.append((j, i))

    spacing = 14
    width = n * spacing + 40
    height = 180
    y_base = height - 30

    svg_parts = [
        f'<svg width="100%" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background: var(--fz-bg-secondary); border-radius: 8px; border: 1px solid var(--fz-border);">'
    ]

    # Draw arcs
    for left, right in pair_list:
        x1 = left * spacing + 20
        x2 = right * spacing + 20
        cx = (x1 + x2) / 2
        r = (x2 - x1) / 2
        svg_parts.append(
            f'<path d="M {x1} {y_base} A {r} {r} 0 0 1 {x2} {y_base}" '
            f'fill="none" stroke="rgba(0, 240, 255, 0.3)" stroke-width="1.5"/>'
        )

    # Draw nucleotides
    nt_colors = {"A": "#FF6B6B", "U": "#4ECDC4", "G": "#FFE66D", "C": "#A78BFA"}
    for i, ch in enumerate(seq.upper()):
        x = i * spacing + 20
        color = nt_colors.get(ch, "#888")
        svg_parts.append(
            f'<text x="{x}" y="{y_base + 14}" text-anchor="middle" '
            f'fill="{color}" font-family="JetBrains Mono, monospace" font-size="11">{ch}</text>'
        )

    svg_parts.append('</svg>')
    st.markdown("".join(svg_parts), unsafe_allow_html=True)


def render_level():
    """Render Level 2: Molecular Origami."""
    st.markdown(f"<h1>🔬 {t('level_2_title')}</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color: var(--fz-text-muted); font-size: 1rem; margin-bottom: 2rem;'>"
        f"{t('level_2_desc')}</p>",
        unsafe_allow_html=True
    )

    # Input options
    tab_input, tab_examples = st.tabs(["✏️ Custom Sequence", "📚 Examples"])

    with tab_examples:
        examples = {
            "tRNA (76 nt)": "GGGCUAUAGCUCAGCUGGGAGAGCGCCUGCUUUGCACGCAGGAGGUCUGCGGUUCGAUCCCGCAUAGCUCCACCA",
            "Hairpin (30 nt)": "GGGGAAAAAACCCCUUUUUGGGGAAAACCC",
            "Simple stem": "GGGGCCCCAAAAGGGGUUUUCCCC",
            "Zika fragment": "AGUUGUUGAUCUGUGUGAAUCAGACUGCGAUCUCA",
        }
        selected_example = st.selectbox("Choose an example:", list(examples.keys()), key="l2_example")
        example_seq = examples[selected_example]
        
        c1, c2 = st.columns(2)
        with c1:
            st.code(example_seq, language=None)
            if st.button("Use this sequence", key="l2_use_example"):
                st.session_state["l2_rna_seq"] = example_seq
        
        with c2:
            if st.button(f"🔍 {t('l2_preview')}", key="l2_preview_btn"):
                with st.spinner("Quick fold..."):
                    bracket = _nussinov_fold(example_seq)
                    st.markdown(f"<div style='font-family: monospace; font-size: 0.75rem;'>{bracket}</div>", unsafe_allow_html=True)
                    _render_arc_diagram(example_seq, bracket)

    with tab_input:
        default_seq = st.session_state.get("l2_rna_seq", "")
        rna_seq = st.text_area(
            t("l2_input_seq"),
            value=default_seq,
            height=100,
            placeholder="GGGGAAAAAACCCC...",
            key="l2_seq_input"
        )

        col1, col2 = st.columns(2)
        with col1:
            min_loop = st.slider("Min loop size", 1, 8, 3, key="l2_min_loop")
        with col2:
            st.markdown(
                f"<div style='padding-top: 1.5rem; color: var(--fz-text-dim); font-size: 0.8rem;'>"
                f"Larger = fewer, more stable loops</div>",
                unsafe_allow_html=True
            )

        if st.button(t("l2_fold"), key="l2_fold_btn", type="primary"):
            if rna_seq.strip():
                clean_seq = "".join(c for c in rna_seq.upper() if c in "AUGC")
                if len(clean_seq) < 4:
                    st.warning("Sequence too short. Enter at least 4 nucleotides.")
                    return

                with st.spinner("Folding..."):
                    bracket = _nussinov_fold(clean_seq, min_loop)
                    num_pairs = _count_pairs(bracket)
                    energy = _approx_energy(num_pairs)

                render_section_divider()

                # Metrics
                c1, c2, c3 = st.columns(3)
                with c1:
                    render_metric_card(t("l2_pairs"), str(num_pairs), "🔗")
                with c2:
                    render_metric_card(t("l2_free_energy"), f"{energy:.1f} kcal/mol", "⚡")
                with c3:
                    render_metric_card("Length", f"{len(clean_seq)} nt", "📏")

                # Dot-bracket display
                st.markdown(f"<h3>{t('l2_structure')}</h3>", unsafe_allow_html=True)
                _render_structure_visual(clean_seq, bracket)

                # Arc diagram
                st.markdown("<h3>Arc Diagram</h3>", unsafe_allow_html=True)
                _render_arc_diagram(clean_seq, bracket)

                # Manual editing sandbox
                st.markdown("---")
                with st.expander("🎨 Manual Editing Sandbox"):
                    st.markdown(
                        "<p style='color: var(--fz-text-muted); font-size: 0.85rem;'>"
                        "Edit the bracket notation to try your own folding. "
                        "Use '(' for 5' pair, ')' for 3' pair, '.' for unpaired.</p>",
                        unsafe_allow_html=True
                    )
                    user_bracket = st.text_input(
                        "Your bracket notation:",
                        value=bracket,
                        key="l2_user_bracket"
                    )
                    if len(user_bracket) == len(clean_seq):
                        _render_structure_visual(clean_seq, user_bracket)
                        user_pairs = _count_pairs(user_bracket)
                        st.info(f"Your folding: {user_pairs} pairs, ~{_approx_energy(user_pairs):.1f} kcal/mol")

                # Gemma analysis
                render_section_divider()
                st.markdown("<h3>🤖 Gemma Analysis</h3>", unsafe_allow_html=True)
                engine = get_gemma_engine()
                lang = st.session_state.get("language", "en")
                diff = st.session_state.get("difficulty", "student")

                analysis = engine.chat(
                    f"Analyze this RNA secondary structure:\n"
                    f"Sequence: {clean_seq[:60]}{'...' if len(clean_seq) > 60 else ''}\n"
                    f"Structure: {bracket[:60]}{'...' if len(bracket) > 60 else ''}\n"
                    f"Base pairs: {num_pairs}, Approx energy: {energy:.1f} kcal/mol\n"
                    f"What can you tell about this structure? Is it stable? What motifs do you see?",
                    difficulty=diff, language=lang,
                    context="Molecular Origami — RNA secondary structure analysis"
                )
                render_gemma_message(analysis)

                # Award points
                if "l2_folded" not in st.session_state:
                    st.session_state["l2_folded"] = True
                    st.session_state["fazena_points"] = st.session_state.get("fazena_points", 0) + 50
                    st.toast("🔬 +50 FP for RNA folding!", icon="⚡")

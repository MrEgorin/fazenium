"""
FAZENIUM — Levels 3-5: 3D Labyrinth
Protein & RNA 3D structure exploration using 3Dmol.js
L3 = Explore, L4 = Compare, L5 = Motifs
"""
import streamlit as st
import requests
from modules.localization import t
from modules.ui_components import render_section_divider, render_gemma_message, render_metric_card
from modules.gemma_engine import get_gemma_engine
from modules.viewer_3d import render_3d_viewer


# ─── PDB Fetcher (Cached) ───────────────────────────
@st.cache_data(show_spinner=False)
def _fetch_pdb(pdb_id: str) -> str | None:
    """Fetch PDB data from RCSB with caching."""
    url = f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            return resp.text
        return None
    except Exception:
        return None


def _extract_chains(pdb_text: str) -> list:
    """Extract unique chain IDs from PDB."""
    chains = set()
    for line in pdb_text.splitlines():
        if line.startswith(("ATOM", "HETATM")) and len(line) > 21:
            chains.add(line[21])
    return sorted(chains)


def _extract_residue_info(pdb_text: str) -> dict:
    """Extract basic residue statistics."""
    residues = set()
    atoms = 0
    hetatm = 0
    for line in pdb_text.splitlines():
        if line.startswith("ATOM"):
            atoms += 1
            if len(line) > 26:
                res = line[17:20].strip()
                chain = line[21]
                resnum = line[22:26].strip()
                residues.add(f"{chain}_{res}_{resnum}")
        elif line.startswith("HETATM"):
            hetatm += 1
    return {
        "residues": len(residues),
        "atoms": atoms,
        "hetatm": hetatm,
        "chains": _extract_chains(pdb_text),
    }


def _render_3d_settings(key_prefix: str):
    """Shared 3D visualization settings."""
    with st.expander("🎨 Visualization Settings", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            style = st.selectbox(t("l3_style"), ["cartoon", "stick", "sphere", "line", "cross"],
                                  index=0, key=f"{key_prefix}_style")
        with c2:
            color = st.selectbox(t("l3_color"), ["spectrum", "chain", "ssType", "Jmol", "white", "lightblue"],
                                  index=0, key=f"{key_prefix}_color")
        with c3:
            show_surface = st.checkbox(t("l3_surface"), value=False, key=f"{key_prefix}_surf")
        with c4:
            spin = st.checkbox(t("l3_spin"), value=False, key=f"{key_prefix}_spin")
    return style, color, show_surface, spin


# ═══════════════════════════════════════════════════════
#  Level 3: Explore
# ═══════════════════════════════════════════════════════
def _render_explore():
    """Level 3: Explore a single 3D structure."""
    st.markdown(f"<h2>🏗️ {t('level_3_title')}</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: var(--fz-text-dim);'>Journey into the atomic heart of biological machinery.</p>", unsafe_allow_html=True)

    tab_pdb, tab_upload, tab_presets = st.tabs(["🔤 PDB ID", "📁 Upload", "📚 Presets"])

    with tab_pdb:
        c1, c2 = st.columns([3, 1])
        with c1:
            pdb_id = st.text_input(t("l3_pdb_id"), value="1BNA", placeholder="e.g. 1BNA, 6LU7, 7V7A", key="l3_pdb_id_input")
        with c2:
            st.markdown("<br>", unsafe_allow_html=True)
            fetch = st.button(t("l3_fetch"), key="l3_fetch_btn", width="stretch")
        if fetch:
            with st.spinner("Fetching..."):
                data = _fetch_pdb(pdb_id)
                if data:
                    st.session_state["l3_pdb_data"] = data
                    st.session_state["l3_pdb_name"] = pdb_id.upper()
                else: st.error(f"Could not fetch {pdb_id}")

    with tab_upload:
        uploaded = st.file_uploader(t("l3_upload_pdb"), type=["pdb", "ent"], key="l3_upload")
        if uploaded:
            st.session_state["l3_pdb_data"] = uploaded.read().decode("utf-8", errors="replace")
            st.session_state["l3_pdb_name"] = uploaded.name

    with tab_presets:
        presets = {"B-DNA (1BNA)": "1BNA", "SARS-CoV-2 Mpro (6LU7)": "6LU7", "Adenylate Kinase (1AKE)": "1AKE", "Hemoglobin (4HHB)": "4HHB", "GFP (1GFL)": "1GFL"}
        sel = st.selectbox("Choose a structure:", list(presets.keys()), key="l3_preset")
        if st.button("Load Preset", key="l3_preset_btn"):
            data = _fetch_pdb(presets[sel])
            if data:
                st.session_state["l3_pdb_data"] = data
                st.session_state["l3_pdb_name"] = presets[sel]

    pdb_data = st.session_state.get("l3_pdb_data")
    if pdb_data:
        style, color, surf, spin = _render_3d_settings("l3")
        info = _extract_residue_info(pdb_data)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: render_metric_card("Structure", st.session_state.get("l3_pdb_name", "Structure"), "🏗️")
        with c2: render_metric_card("Residues", str(info["residues"]), "🧬")
        with c3: render_metric_card("Atoms", str(info["atoms"]), "⚛️")
        with c4: render_metric_card("Chains", ", ".join(info["chains"]), "🔗")

        render_3d_viewer(pdb_data, style, color, surf, spin)

        with st.expander("🤖 Discuss with Gemma"):
            # Use streaming chat for analysis
            q = st.text_input("Ask Gemma about this structure:", key="l3_gemma_q")
            if st.button("Ask", key="l3_gemma_ask"):
                engine = get_gemma_engine()
                placeholder = st.empty()
                full_res = ""
                for chunk in engine.stream_chat(f"About PDB {st.session_state.get('l3_pdb_name')}: {q}", context="3D Exploration"):
                    full_res += chunk
                    placeholder.markdown(f"<div class='gemma-msg ai'>{full_res}</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
#  Level 4: Compare
# ═══════════════════════════════════════════════════════
def _render_compare():
    """Level 4: Compare two structures side by side."""
    st.markdown(f"<h2>🔍 {t('level_4_title')}</h2>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        pdb1 = st.text_input("Structure A:", value="6LU7", key="l4_pdb1")
        if st.button("Fetch A", key="l4_fetch1"):
            st.session_state["l4_data1"] = _fetch_pdb(pdb1)
    with col_b:
        pdb2 = st.text_input("Structure B:", value="7V7A", key="l4_pdb2")
        if st.button("Fetch B", key="l4_fetch2"):
            st.session_state["l4_data2"] = _fetch_pdb(pdb2)

    d1 = st.session_state.get("l4_data1")
    d2 = st.session_state.get("l4_data2")

    if d1 and d2:
        style, color, surf, spin = _render_3d_settings("l4")
        v_a, v_b = st.columns(2)
        with v_a:
            st.markdown(f"**{pdb1.upper()}**")
            render_3d_viewer(d1, style, color, surf, spin, height=400)
        with v_b:
            st.markdown(f"**{pdb2.upper()}**")
            render_3d_viewer(d2, style, color, surf, spin, height=400)


# ═══════════════════════════════════════════════════════
#  Level 5: Motifs
# ═══════════════════════════════════════════════════════
def _render_motifs():
    """Level 5: Find structural motifs."""
    st.markdown(f"<h2>🧩 {t('level_5_title')}</h2>", unsafe_allow_html=True)
    
    pdb_id = st.text_input("Analyze Motifs (PDB):", value="1AKE", key="l5_pdb")
    if st.button("Analyze", key="l5_btn"):
        st.session_state["l5_data"] = _fetch_pdb(pdb_id)

    data = st.session_state.get("l5_data")
    if data:
        style, color, surf, spin = _render_3d_settings("l5")
        
        helices = sum(1 for line in data.splitlines() if line.startswith("HELIX"))
        sheets = sum(1 for line in data.splitlines() if line.startswith("SHEET"))
        
        c1, c2 = st.columns(2)
        with c1: render_metric_card("α-Helices", str(helices), "🌀")
        with c2: render_metric_card("β-Sheets", str(sheets), "📄")

        render_3d_viewer(data, style, color, surf, spin)


def render_level(sub_level: int = 3):
    if sub_level == 3: _render_explore()
    elif sub_level == 4: _render_compare()
    elif sub_level == 5: _render_motifs()

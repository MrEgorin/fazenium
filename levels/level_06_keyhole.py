"""
FAZENIUM — Level 6: The Keyhole
Binding site detection simulator
"""
import streamlit as st
import requests
from modules.localization import t
from modules.ui_components import render_section_divider, render_gemma_message, render_metric_card
from modules.gemma_engine import get_gemma_engine
from modules.viewer_3d import render_pocket_viewer as _render_pocket_viewer_js


def _fetch_pdb(pdb_id: str) -> str | None:
    url = f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb"
    try:
        resp = requests.get(url, timeout=15)
        return resp.text if resp.status_code == 200 else None
    except Exception:
        return None


def _detect_pockets(pdb_text: str, num_pockets: int = 3):
    """Simplified pocket detection based on spatial clustering of residues.
    Returns list of pocket dicts with center coordinates and residue lists."""
    from collections import defaultdict
    import math

    # Parse CA atoms
    ca_atoms = []
    for line in pdb_text.splitlines():
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            try:
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                res_name = line[17:20].strip()
                res_num = line[22:26].strip()
                chain = line[21]
                ca_atoms.append({
                    "x": x, "y": y, "z": z,
                    "res": f"{chain}:{res_name}{res_num}",
                    "res_name": res_name
                })
            except (ValueError, IndexError):
                continue

    if len(ca_atoms) < 10:
        return []

    # Simple k-means-like clustering for pocket centers
    # Use geometric center subdivisions
    cx = sum(a["x"] for a in ca_atoms) / len(ca_atoms)
    cy = sum(a["y"] for a in ca_atoms) / len(ca_atoms)
    cz = sum(a["z"] for a in ca_atoms) / len(ca_atoms)

    # Create candidate pocket centers by looking at regions with many nearby residues
    grid = defaultdict(list)
    grid_size = 8.0
    for atom in ca_atoms:
        gx = int(atom["x"] / grid_size)
        gy = int(atom["y"] / grid_size)
        gz = int(atom["z"] / grid_size)
        grid[(gx, gy, gz)].append(atom)

    # Sort grid cells by density
    cells = sorted(grid.items(), key=lambda x: len(x[1]), reverse=True)

    pockets = []
    used_cells = set()
    for (gx, gy, gz), atoms in cells:
        if len(pockets) >= num_pockets:
            break
        if (gx, gy, gz) in used_cells:
            continue

        # Mark nearby cells as used
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    used_cells.add((gx + dx, gy + dy, gz + dz))

        pocket_center = {
            "x": sum(a["x"] for a in atoms) / len(atoms),
            "y": sum(a["y"] for a in atoms) / len(atoms),
            "z": sum(a["z"] for a in atoms) / len(atoms),
        }

        # Find residues within 10Å of pocket center
        pocket_residues = []
        for atom in ca_atoms:
            dist = math.sqrt(
                (atom["x"] - pocket_center["x"]) ** 2 +
                (atom["y"] - pocket_center["y"]) ** 2 +
                (atom["z"] - pocket_center["z"]) ** 2
            )
            if dist < 10.0:
                pocket_residues.append(atom["res"])

        # Druggability heuristic: hydrophobic + polar mix
        druggability = min(1.0, len(pocket_residues) / 25.0)

        pockets.append({
            "center": pocket_center,
            "residues": pocket_residues[:20],
            "druggability": round(druggability, 2),
            "size": len(pocket_residues),
        })

    return pockets


def _render_pocket_viewer(pdb_text: str, pockets: list):
    """Render 3D view with binding sites highlighted using 3Dmol.js."""
    _render_pocket_viewer_js(pdb_text, pockets)


def render_level():
    """Render Level 6: The Keyhole."""
    st.markdown(f"<h1>🔑 {t('level_6_title')}</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color: var(--fz-text-muted); font-size: 1rem; margin-bottom: 1rem;'>"
        f"{t('level_6_desc')}</p>",
        unsafe_allow_html=True
    )

    # Pocket Primer (Static Knowledge)
    with st.expander(f"📚 {t('l6_kb_title')}", expanded=True):
        st.markdown(
            f"<div style='font-size: 0.95rem; line-height: 1.6; color: var(--fz-text-muted);'>"
            f"{t('l6_kb_text')}</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "- **Shape complementarity:** The ligand must fit physically into the pocket.\n"
            "- **Chemical complementarity:** Functional groups must align (H-bond donors to acceptors, etc.).\n"
            "- **Druggability:** Not all pockets are good targets; some are too shallow or too large."
        )

    render_section_divider()

    col_in, col_set = st.columns([2, 1])

    with col_in:
        pdb_id = st.text_input("PDB ID:", value="6LU7", key="l6_pdb")
        if st.button(t("l6_detect"), key="l6_detect_btn", type="primary"):
            with st.spinner("Analyzing binding sites..."):
                data = _fetch_pdb(pdb_id)
                if data:
                    st.session_state["l6_pdb_data"] = data
                    st.session_state["l6_pockets"] = _detect_pockets(data)
                else:
                    st.error(f"Cannot fetch {pdb_id}")

    with col_set:
        num_pockets = st.slider("Max pockets to find:", 1, 6, 3, key="l6_num_pockets")

    data = st.session_state.get("l6_pdb_data")
    pockets = st.session_state.get("l6_pockets")

    if data and pockets:
        render_section_divider()

        # Pocket metrics
        cols = st.columns(len(pockets))
        for i, pocket in enumerate(pockets):
            with cols[i]:
                score_pct = f"{pocket['druggability'] * 100:.0f}%"
                render_metric_card(
                    f"{t('l6_pocket')} {i + 1}",
                    score_pct,
                    f"🎯 {pocket['size']} res"
                )

        # 3D viewer
        _render_pocket_viewer(data, pockets)

        # Pocket details
        for i, pocket in enumerate(pockets):
            with st.expander(f"🔑 {t('l6_pocket')} {i + 1} — {t('l6_residues')}"):
                st.markdown(
                    f"<div style='font-family: var(--fz-font-mono); font-size: 0.8rem; "
                    f"color: var(--fz-text-muted); line-height: 2;'>"
                    f"{' · '.join(pocket['residues'])}</div>",
                    unsafe_allow_html=True
                )
                st.progress(pocket["druggability"])
                st.caption(f"{t('l6_druggability')}: {pocket['druggability']:.2f}")

        # Manual pocket marking
        render_section_divider()
        with st.expander("🎯 Mark Your Own Pocket"):
            st.markdown(
                "<p style='color: var(--fz-text-muted); font-size: 0.85rem;'>"
                "Enter approximate coordinates for your predicted binding site.</p>",
                unsafe_allow_html=True
            )
            uc1, uc2, uc3 = st.columns(3)
            with uc1:
                ux = st.number_input("X:", value=0.0, key="l6_ux")
            with uc2:
                uy = st.number_input("Y:", value=0.0, key="l6_uy")
            with uc3:
                uz = st.number_input("Z:", value=0.0, key="l6_uz")

            if st.button("Show my pocket", key="l6_show_mine"):
                user_pocket = [{"center": {"x": ux, "y": uy, "z": uz},
                               "residues": ["User-defined"], "druggability": 0.5, "size": 0}]
                _render_pocket_viewer(data, pockets + user_pocket)

        # Gemma
        render_section_divider()
        engine = get_gemma_engine()
        lang = st.session_state.get("language", "en")
        diff = st.session_state.get("difficulty", "student")
        pocket_info = ", ".join(
            f"P{i+1}: {p['size']} residues, druggability={p['druggability']}"
            for i, p in enumerate(pockets)
        )
        analysis = engine.chat(
            f"I found these binding pockets in {pdb_id}: {pocket_info}. "
            f"Which pocket is most promising for drug design and why?",
            difficulty=diff, language=lang,
            context="The Keyhole — binding site detection and analysis"
        )
        render_gemma_message(analysis)

        if "l6_done" not in st.session_state:
            st.session_state["l6_done"] = True
            st.session_state["fazena_points"] = st.session_state.get("fazena_points", 0) + 75
            st.toast("🔑 +75 FP for binding site detection!", icon="⚡")

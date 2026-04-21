"""
FAZENIUM — Levels 7-8: Molecular Constructor
SMILES-based ligand builder with RDKit
L7 = Build & visualize, L8 = Optimize & check drug-likeness
"""
import json
import os
import io
import streamlit as st
from modules.localization import t
from modules.ui_components import render_section_divider, render_gemma_message, render_metric_card
from modules.gemma_engine import get_gemma_engine
from config import DATA_DIR

try:
    from rdkit import Chem
    from rdkit.Chem import Draw, Descriptors, AllChem
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False


def _load_fragments():
    path = os.path.join(DATA_DIR, "fragments.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _mol_properties(mol) -> dict:
    """Calculate molecular properties."""
    return {
        "MW": round(Descriptors.MolWt(mol), 2),
        "LogP": round(Descriptors.MolLogP(mol), 2),
        "HBD": Descriptors.NumHDonors(mol),
        "HBA": Descriptors.NumHAcceptors(mol),
        "TPSA": round(Descriptors.TPSA(mol), 2),
        "RotBonds": Descriptors.NumRotatableBonds(mol),
        "Rings": Descriptors.RingCount(mol),
        "HeavyAtoms": mol.GetNumHeavyAtoms(),
    }


def _lipinski_check(props: dict) -> tuple:
    """Check Lipinski's Rule of 5. Returns (pass, violations)."""
    violations = []
    if props["MW"] > 500:
        violations.append(f"MW={props['MW']} > 500")
    if props["LogP"] > 5:
        violations.append(f"LogP={props['LogP']} > 5")
    if props["HBD"] > 5:
        violations.append(f"HBD={props['HBD']} > 5")
    if props["HBA"] > 10:
        violations.append(f"HBA={props['HBA']} > 10")
    return len(violations) <= 1, violations


def _render_mol_image(mol, width=400, height=300):
    """Render RDKit 2D depiction."""
    AllChem.Compute2DCoords(mol)
    img = Draw.MolToImage(mol, size=(width, height))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), width="stretch")


# ═══════════════════════════════════════════════════════
#  Level 7: Basic Constructor
# ═══════════════════════════════════════════════════════
def _render_constructor():
    """Level 7: Build molecules with SMILES."""
    st.markdown(f"<h1>⚗️ {t('level_7_title')}</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color: var(--fz-text-muted); font-size: 1rem; margin-bottom: 2rem;'>"
        f"{t('level_7_desc')}</p>",
        unsafe_allow_html=True
    )

    if not HAS_RDKIT:
        st.error("RDKit not installed. Install with: pip install rdkit")
        return

    tab_build, tab_fragments = st.tabs(["🧪 Free Build", f"🧩 {t('l7_fragments')}"])

    with tab_fragments:
        fragments = _load_fragments()
        categories = sorted(set(f["category"] for f in fragments))
        sel_cat = st.selectbox("Category:", categories, key="l7_frag_cat")

        filtered = [f for f in fragments if f["category"] == sel_cat]
        cols = st.columns(3)
        for i, frag in enumerate(filtered):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="fazena-card" style="padding: 1rem; min-height: 90px;">
                    <div style="font-family: var(--fz-font-heading); font-size: 0.8rem;
                         color: var(--fz-accent); letter-spacing: 0.5px;">{frag['name']}</div>
                    <div style="font-family: var(--fz-font-mono); font-size: 0.75rem;
                         color: var(--fz-text-muted); margin-top: 4px;">{frag['smiles']}</div>
                    <div style="font-size: 0.7rem; color: var(--fz-text-dim);
                         margin-top: 4px;">{frag['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Use", key=f"l7_use_{frag['smiles']}"):
                    current = st.session_state.get("l7_smiles", "")
                    st.session_state["l7_smiles"] = current + frag["smiles"]
                    st.rerun()

    with tab_build:
        default_smiles = st.session_state.get("l7_smiles", "c1ccccc1")
        smiles = st.text_input(
            t("l7_smiles_input"),
            value=default_smiles,
            key="l7_smiles_input",
            placeholder="e.g. c1ccccc1, CCO, CC(=O)Nc1ccc(O)cc1"
        )

        if st.button(t("l7_draw"), key="l7_draw_btn", type="primary"):
            st.session_state["l7_active_smiles"] = smiles

        active = st.session_state.get("l7_active_smiles", "")
        if active:
            mol = Chem.MolFromSmiles(active)
            if mol is None:
                st.error(f"Invalid SMILES: {active}")
            else:
                render_section_divider()

                col_img, col_props = st.columns([1, 1])

                with col_img:
                    st.markdown("**2D Structure**")
                    _render_mol_image(mol)
                    st.markdown(
                        f"<div style='font-family: var(--fz-font-mono); font-size: 0.8rem; "
                        f"color: var(--fz-text-dim); text-align: center; margin-top: 0.5rem;'>"
                        f"SMILES: {active}</div>",
                        unsafe_allow_html=True
                    )

                with col_props:
                    st.markdown(f"**{t('l7_properties')}**")
                    props = _mol_properties(mol)

                    for key, label_key in [
                        ("MW", "l7_mw"), ("LogP", "l7_logp"),
                        ("HBD", "l7_hbd"), ("HBA", "l7_hba"),
                        ("TPSA", "l7_tpsa")
                    ]:
                        col_l, col_v = st.columns([2, 1])
                        with col_l:
                            st.markdown(
                                f"<span style='color: var(--fz-text-muted); font-size: 0.85rem;'>"
                                f"{t(label_key)}</span>",
                                unsafe_allow_html=True
                            )
                        with col_v:
                            st.markdown(
                                f"<span style='color: var(--fz-accent); font-family: var(--fz-font-mono); "
                                f"font-size: 0.9rem;'>{props[key]}</span>",
                                unsafe_allow_html=True
                            )

                    st.markdown("---")

                    # Lipinski
                    passes, violations = _lipinski_check(props)
                    status = t("l7_pass") if passes else t("l7_fail")
                    badge_cls = "success" if passes else "error"
                    st.markdown(
                        f"<div style='margin-top: 0.5rem;'>"
                        f"<span class='status-badge {badge_cls}'>{t('l7_lipinski')}: {status}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    if violations:
                        for v in violations:
                            st.markdown(f"- ⚠️ {v}")

                # Gemma critique
                render_section_divider()
                st.markdown("**🤖 Gemma Critique**")
                engine = get_gemma_engine()
                lang = st.session_state.get("language", "en")
                diff = st.session_state.get("difficulty", "student")
                critique = engine.get_molecule_critique(active, props, diff, lang)
                render_gemma_message(critique)

                if "l7_built" not in st.session_state:
                    st.session_state["l7_built"] = True
                    st.session_state["fazena_points"] = st.session_state.get("fazena_points", 0) + 75
                    st.toast("⚗️ +75 FP for molecule design!", icon="⚡")


# ═══════════════════════════════════════════════════════
#  Level 8: Advanced Constructor
# ═══════════════════════════════════════════════════════
def _render_advanced():
    """Level 8: Optimize molecules and compare drug-likeness."""
    st.markdown(f"<h1>💊 {t('level_8_title')}</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color: var(--fz-text-muted); font-size: 1rem; margin-bottom: 2rem;'>"
        f"{t('level_8_desc')}</p>",
        unsafe_allow_html=True
    )

    if not HAS_RDKIT:
        st.error("RDKit not installed.")
        return

    st.markdown("### Compare Multiple Molecules")
    st.markdown(
        "<p style='color: var(--fz-text-muted); font-size: 0.85rem;'>"
        "Enter SMILES (one per line) to compare their properties side by side.</p>",
        unsafe_allow_html=True
    )

    smiles_text = st.text_area(
        "SMILES (one per line):",
        value="CC(=O)Nc1ccc(O)cc1\nCC(C)Cc1ccc(cc1)C(C)C(=O)O\nCC(=O)Oc1ccccc1C(=O)O",
        height=120,
        key="l8_multi_smiles"
    )

    if st.button("Compare All", key="l8_compare", type="primary"):
        lines = [l.strip() for l in smiles_text.strip().splitlines() if l.strip()]

        results = []
        for smi in lines:
            mol = Chem.MolFromSmiles(smi)
            if mol:
                props = _mol_properties(mol)
                passes, viols = _lipinski_check(props)
                results.append({
                    "SMILES": smi,
                    "mol": mol,
                    "props": props,
                    "lipinski": passes,
                    "violations": viols,
                })

        if not results:
            st.error("No valid SMILES found.")
            return

        # Comparison table
        render_section_divider()
        cols = st.columns(len(results))
        for i, r in enumerate(results):
            with cols[i]:
                _render_mol_image(r["mol"], 250, 200)
                st.markdown(
                    f"<div style='font-family: var(--fz-font-mono); font-size: 0.7rem; "
                    f"color: var(--fz-text-dim); text-align: center; word-break: break-all;'>"
                    f"{r['SMILES']}</div>",
                    unsafe_allow_html=True
                )
                badge = "success" if r["lipinski"] else "error"
                label = t("l7_pass") if r["lipinski"] else t("l7_fail")
                st.markdown(
                    f"<div style='text-align: center; margin-top: 8px;'>"
                    f"<span class='status-badge {badge}'>{label}</span></div>",
                    unsafe_allow_html=True
                )

        # Properties comparison
        st.markdown("### Property Comparison")
        import pandas as pd
        df_data = []
        for r in results:
            row = {"SMILES": r["SMILES"][:30] + "..." if len(r["SMILES"]) > 30 else r["SMILES"]}
            row.update(r["props"])
            row["Lipinski"] = "✅" if r["lipinski"] else "❌"
            df_data.append(row)
        df = pd.DataFrame(df_data)
        st.dataframe(df, width="stretch", hide_index=True)

        if "l8_compared" not in st.session_state:
            st.session_state["l8_compared"] = True
            st.session_state["fazena_points"] = st.session_state.get("fazena_points", 0) + 100
            st.toast("💊 +100 FP for molecule optimization!", icon="⚡")


def render_level(sub_level: int = 7):
    if sub_level == 7:
        _render_constructor()
    elif sub_level == 8:
        _render_advanced()

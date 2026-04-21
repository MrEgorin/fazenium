import random
import math
import pandas as pd
import streamlit as st
from modules.localization import t
from modules.ui_components import render_section_divider, render_gemma_message, render_metric_card
from modules.gemma_engine import get_gemma_engine

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, AllChem
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False

from modules.viewer_3d import render_md_trajectory, render_docking_result


@st.cache_data(show_spinner=False)
def _simulate_docking_score(smiles: str) -> dict:
    """Simulate a realistic docking simulation with RDKit 3D generation."""
    if not HAS_RDKIT:
        return {"score": round(random.uniform(-9.0, -3.0), 2), "simulated": True, "error": "RDKit missing"}

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"score": 0.0, "error": "Invalid SMILES"}

    mol = Chem.AddHs(mol)
    try:
        AllChem.EmbedMolecule(mol, randomSeed=42)
        AllChem.MMFFOptimizeMolecule(mol)
    except Exception:
        pass
        
    mol_block = Chem.MolToMolBlock(mol)
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    hba = Descriptors.NumHAcceptors(mol)
    hbd = Descriptors.NumHDonors(mol)

    base_score = -5.0
    base_score -= Descriptors.RingCount(mol) * 0.5
    base_score -= min(hba, 5) * 0.3
    base_score -= min(hbd, 3) * 0.2

    if 200 < mw < 500: base_score -= 1.0
    if 1 < logp < 4: base_score -= 0.8

    noise = random.gauss(0, 0.4)
    score = round(base_score + noise, 2)
    rt = 0.592
    ki = math.exp(score / rt) * 1e9
    
    return {
        "score": score,
        "ki_nm": round(ki, 2),
        "mw": round(mw, 1),
        "logp": round(logp, 2),
        "mol_block": mol_block,
        "h_bonds": min(hba + hbd, random.randint(1, 5)),
        "vdw_energy": round(score * 0.7, 2),
        "elec_energy": round(score * 0.3, 2)
    }


@st.cache_data(show_spinner=False)
def _generate_trajectory(pdb_text: str, frames: int = 20) -> str:
    """Generate a multi-model PDB simulating molecular dynamics."""
    lines = pdb_text.splitlines()
    atoms = [line for line in lines if line.startswith("ATOM")]
    trajectory = ""
    for frame in range(1, frames + 1):
        trajectory += f"MODEL {frame}\n"
        for atom in atoms:
            try:
                x = float(atom[30:38])
                y = float(atom[38:46])
                z = float(atom[46:54])
                factor = math.sin(frame * 0.3) * 0.4 + random.uniform(-0.15, 0.15)
                nx, ny, nz = x + factor, y + factor, z + factor
                trajectory += atom[:30] + f"{nx:8.3f}{ny:8.3f}{nz:8.3f}" + atom[54:] + "\n"
            except:
                trajectory += atom + "\n"
        trajectory += "ENDMDL\n"
    return trajectory


@st.cache_data(show_spinner=False)
def _fetch_pdb(pdb_id: str) -> str | None:
    import requests
    try:
        resp = requests.get(f"https://files.rcsb.org/download/{pdb_id}.pdb", timeout=10)
        return resp.text if resp.status_code == 200 else None
    except: return None


def render_level():
    st.markdown(f"<h1>⚡ {t('level_9_title')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: var(--fz-text-muted); font-size: 1rem; margin-bottom: 2rem;'>{t('level_9_desc')}</p>", unsafe_allow_html=True)

    tab_dock, tab_md = st.tabs(["🎯 Docking Simulation", "🌊 Molecular Dynamics"])

    with tab_dock:
        st.markdown("<p style='color: var(--fz-text-muted); font-size: 0.85rem;'>Simulate docking against a protein target. Find the best ligand!</p>", unsafe_allow_html=True)
        
        presets = {"Paracetamol": "CC(=O)Nc1ccc(O)cc1", "Ibuprofen": "CC(C)Cc1ccc(cc1)C(C)C(=O)O", "Caffeine": "Cn1c(=O)c2c(ncn2C)n(C)c1=O", "Custom": ""}
        sel_preset = st.selectbox("Choose a ligand:", list(presets.keys()), key="l9_preset")
        smiles = st.text_input("SMILES:", key="l9_smiles", value=presets[sel_preset]) if sel_preset == "Custom" else presets[sel_preset]

        if st.button(t("l9_run_dock"), key="l9_dock_btn", type="primary"):
            if smiles:
                with st.spinner("Docking..."):
                    result = _simulate_docking_score(smiles)
                
                c1, c2, c3 = st.columns(3)
                with c1: render_metric_card(t("l9_score"), f"{result['score']} kcal/mol", "🎯")
                with c2: render_metric_card(t("l9_affinity"), f"{result['ki_nm']:.1f} nM", "💊")
                with c3: render_metric_card("Rating", "⭐⭐⭐ Excellent" if result['score'] < -8 else "⭐⭐ Good", "📊")

                with st.expander("🔬 Interaction Details"):
                    st.write(f"- H-Bonds: {result['h_bonds']}, vdW: {result['vdw_energy']} kcal/mol, Elec: {result['elec_energy']} kcal/mol")

                st.markdown("### 3D Complex")
                rec_pdb = _fetch_pdb("6LU7")
                if rec_pdb: render_docking_result(rec_pdb, result["mol_block"])

    with tab_md:
        st.markdown(f"<h3>{t('sb_lesson_title')}</h3>", unsafe_allow_html=True)
        st.info("Molecular Dynamics (MD) simulates the movement of atoms over time using Newton's laws. It allows us to observe how a protein 'breathes' and how stable a drug-protein complex is.")

        pdb_options = {
            t("sb_obj_mpro"): "6LU7",
            t("sb_obj_dna"): "1BNA",
            t("sb_obj_trna"): "1TRA",
            t("sb_obj_ribosome"): "1UL1",
            t("sb_obj_complex"): "1AQ1"
        }
        sel_obj = st.selectbox(t("sb_pdb_select"), list(pdb_options.keys()))
        pdb_id = pdb_options[sel_obj]

        duration_ns = st.slider("Simulation Duration (ns)", 10, 500, 150)

        if st.button(t("l9_dynamics"), key="l9_md_btn", type="primary"):
            with st.spinner("Calculating trajectory..."):
                pdb_data = _fetch_pdb(pdb_id)
                if pdb_data:
                    trajectory = _generate_trajectory(pdb_data, frames=20)
                    
                    # Simulated Data Generation
                    steps = 20
                    time_axis = [i * (duration_ns / steps) for i in range(steps)]
                    
                    st.markdown("### Live Trajectory Visualization")
                    render_md_trajectory(trajectory)
                    
                    render_section_divider()
                    st.markdown(f"### {t('dash_progress')} Metrics")
                    
                    col_plots = st.columns(3)
                    
                    # RG plot
                    with col_plots[0]:
                        rg_vals = [24.5 + math.sin(i*0.5)*0.2 + random.uniform(-0.1, 0.1) for i in range(steps)]
                        df_rg = pd.DataFrame({"ns": time_axis, "Rg (Å)": rg_vals})
                        st.line_chart(df_rg.set_index("ns"))
                        st.caption(t("sb_rg"))
                    
                    # SASA plot
                    with col_plots[1]:
                        sasa_vals = [12000 + math.cos(i*0.3)*200 + random.uniform(-100, 100) for i in range(steps)]
                        df_sasa = pd.DataFrame({"ns": time_axis, "SASA (Å²)": sasa_vals})
                        st.line_chart(df_sasa.set_index("ns"))
                        st.caption(t("sb_sasa"))
                        
                    # RMSD plot
                    with col_plots[2]:
                        rmsd_vals = [0.1 * math.sqrt(i) + random.uniform(0, 0.2) for i in range(steps)]
                        df_rmsd = pd.DataFrame({"ns": time_axis, "RMSD (Å)": rmsd_vals})
                        st.line_chart(df_rmsd.set_index("ns"))
                        st.caption("RMSD")

                    # Quick Guides
                    with st.expander("💡 Understanding these metrics"):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown(f"**{t('sb_rg')}**: {t('sb_rg_desc')}")
                            st.markdown(f"**{t('sb_sasa')}**: {t('sb_sasa_desc')}")
                        with c2:
                            st.markdown(f"**RMSD**: {t('sb_rmsd_desc')}")
                            st.markdown(f"**{t('sb_hbonds')}**: {t('sb_hbonds_desc')}")

            # Award points
            if "l9_done" not in st.session_state:
                st.session_state["l9_done"] = True
                st.session_state["fazena_points"] = st.session_state.get("fazena_points", 0) + 100
                st.toast("⚡ +100 FP for running high-performance simulation!", icon="🧬")

"""
FAZENIUM — Level 10: Open World
RAG-powered news feed and database cross-referencing
"""
import streamlit as st
import json
from modules.localization import t
from modules.ui_components import render_section_divider, render_gemma_message, render_metric_card
from modules.gemma_engine import get_gemma_engine


# ─── Static breakthrough database (2024-2026) ────────
_BREAKTHROUGHS = [
    {
        "year": 2026,
        "title": {"en": "AI-Designed Antibiotic Halicin Enters Phase II Trials",
                  "ua": "AI-розроблений антибіотик Галіцин входить у фазу II",
                  "de": "KI-entwickeltes Antibiotikum Halicin tritt in Phase II ein"},
        "summary": {"en": "The first AI-discovered antibiotic, Halicin, advances in clinical trials after showing efficacy against drug-resistant bacteria.",
                     "ua": "Перший антибіотик, відкритий ШІ, Галіцин, просувається у клінічних випробуваннях після демонстрації ефективності проти стійких бактерій.",
                     "de": "Das erste KI-entdeckte Antibiotikum Halicin schreitet nach erfolgreichen Tests gegen resistente Bakterien in klinischen Studien voran."},
        "tags": ["AI", "antibiotics", "drug-resistance"],
    },
    {
        "year": 2025,
        "title": {"en": "AlphaFold 3 Accurately Predicts Drug-Protein Interactions",
                  "ua": "AlphaFold 3 точно передбачає взаємодії ліки-білок",
                  "de": "AlphaFold 3 sagt Medikament-Protein-Interaktionen genau vorher"},
        "summary": {"en": "DeepMind's AlphaFold 3 can now predict how drugs bind to proteins with near-experimental accuracy, transforming virtual screening.",
                     "ua": "AlphaFold 3 від DeepMind тепер може передбачати, як ліки зв'язуються з білками з майже експериментальною точністю.",
                     "de": "DeepMinds AlphaFold 3 kann nun vorhersagen, wie Medikamente an Proteine binden, mit nahezu experimenteller Genauigkeit."},
        "tags": ["AlphaFold", "protein-structure", "virtual-screening"],
    },
    {
        "year": 2025,
        "title": {"en": "RNA-Targeting Small Molecules Show Promise for ALS",
                  "ua": "Малі молекули-мішені РНК показують перспективи для БАС",
                  "de": "RNA-zielgerichtete kleine Moleküle zeigen Versprechen für ALS"},
        "summary": {"en": "A new class of small molecules that target toxic RNA repeats shows significant efficacy in ALS mouse models.",
                     "ua": "Новий клас малих молекул, що націлені на токсичні повтори РНК, демонструє значну ефективність на моделях БАС.",
                     "de": "Eine neue Klasse kleiner Moleküle, die toxische RNA-Wiederholungen angreifen, zeigt signifikante Wirksamkeit in ALS-Mausmodellen."},
        "tags": ["RNA", "ALS", "small-molecules"],
    },
    {
        "year": 2024,
        "title": {"en": "CRISPR Gene Therapy Approved for Sickle Cell Disease",
                  "ua": "CRISPR генна терапія схвалена для серповидноклітинної анемії",
                  "de": "CRISPR-Gentherapie für Sichelzellenanämie zugelassen"},
        "summary": {"en": "Vertex Pharmaceuticals' CRISPR-based therapy Casgevy receives FDA approval, marking a historic milestone for gene editing therapies.",
                     "ua": "CRISPR-терапія Casgevy від Vertex Pharmaceuticals отримує схвалення FDA — історична подія для генної терапії.",
                     "de": "Die CRISPR-basierte Therapie Casgevy von Vertex Pharmaceuticals erhält FDA-Zulassung — ein historischer Meilenstein."},
        "tags": ["CRISPR", "gene-therapy", "FDA"],
    },
    {
        "year": 2026,
        "title": {"en": "Generative Chemistry Models Create Drug Candidates 10× Faster",
                  "ua": "Генеративні хімічні моделі створюють кандидати ліків у 10 разів швидше",
                  "de": "Generative Chemie-Modelle erzeugen Wirkstoffkandidaten 10× schneller"},
        "summary": {"en": "Combining LLMs with molecular generation tools, pharma companies report 10× speedup in lead optimization, cutting timelines from years to months.",
                     "ua": "Поєднуючи LLM з інструментами молекулярної генерації, фармкомпанії повідомляють про 10-кратне прискорення оптимізації лідів.",
                     "de": "Durch die Kombination von LLMs mit molekularen Generierungswerkzeugen berichten Pharmaunternehmen von einer 10-fachen Beschleunigung der Leitstruktur-Optimierung."},
        "tags": ["LLM", "generative-chemistry", "lead-optimization"],
    },
    {
        "year": 2025,
        "title": {"en": "First De Novo AI-Designed Drug Reaches Phase I Clinical Trial",
                  "ua": "Перший de novo ШІ-дизайнований лік досягає фази I клінічних випробувань",
                  "de": "Erstes de novo KI-designtes Medikament erreicht Phase I"},
        "summary": {"en": "Insilico Medicine's AI-designed molecule INS018_055 for IPF shows promising safety data in Phase I, validating end-to-end AI drug design.",
                     "ua": "ШІ-дизайнована молекула INS018_055 від Insilico Medicine для ІЛФ демонструє обнадійливі дані безпеки у фазі I.",
                     "de": "Insilico Medicines KI-designtes Molekül INS018_055 für IPF zeigt vielversprechende Sicherheitsdaten in Phase I."},
        "tags": ["AI", "de-novo", "clinical-trial"],
    },
]


def render_level():
    """Render Level 10: Open World."""
    st.markdown(f"<h1>🌍 {t('level_10_title')}</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color: var(--fz-text-muted); font-size: 1rem; margin-bottom: 2rem;'>"
        f"{t('level_10_desc')}</p>",
        unsafe_allow_html=True
    )

    tab_news, tab_search, tab_report = st.tabs([
        f"📰 {t('l10_news')}",
        f"🔍 {t('l10_search')}",
        f"📋 {t('l10_export')}"
    ])

    lang = st.session_state.get("language", "en")
    diff = st.session_state.get("difficulty", "student")

    with tab_news:
        # Filter by tags
        all_tags = set()
        for b in _BREAKTHROUGHS:
            all_tags.update(b["tags"])
        all_tags = sorted(all_tags)

        selected_tags = st.multiselect("Filter by topic:", all_tags, key="l10_tags")

        filtered = _BREAKTHROUGHS
        if selected_tags:
            filtered = [b for b in _BREAKTHROUGHS if any(tag in b["tags"] for tag in selected_tags)]

        # Article Reader State
        selected_article_idx = st.session_state.get("l10_article_idx", None)

        if selected_article_idx is not None:
            art = _BREAKTHROUGHS[selected_article_idx]
            if st.button(f"⬅️ {t('l10_back')}"):
                st.session_state["l10_article_idx"] = None
                st.rerun()
            
            st.markdown(f"## {art['title'].get(lang, art['title']['en'])}")
            st.markdown(f"**Year:** {art['year']} | **Topics:** {', '.join(art['tags'])}")
            render_section_divider()
            
            # Simulated long content
            st.markdown(f"""
            <div style="font-size: 1.1rem; line-height: 1.8; color: var(--fz-text);">
                {art['summary'].get(lang, art['summary']['en'])}
                <br><br>
                This breakthrough represents a significant shift in computational biology. 
                Researchers utilized distributed computing and advanced generative models to 
                explore a chemical space of over 10^60 possible molecules. 
                The integration of RAG (Retrieval-Augmented Generation) allowed the AI to 
                cross-reference findings with existing literature in real-time, reducing 
                false positives by 45%.
                <br><br>
                Future directions include expanding this approach to multi-target drug design 
                and personalized medicine where specific genetic variants are considered.
            </div>
            """, unsafe_allow_html=True)
            
            # Discuss with Gemma about THIS article
            st.markdown("---")
            st.markdown(f"### 💬 Discuss this with Gemma")
            q = st.text_input("Ask a question about this article:", key="l10_art_q")
            if st.button("Analyze", key="l10_art_btn"):
                engine = get_gemma_engine()
                ans = engine.chat(f"Context: {art['title']['en']}. Question: {q}", difficulty=diff, language=lang)
                render_gemma_message(ans)

        else:
            for i, b in enumerate(filtered):
                title = b["title"].get(lang, b["title"]["en"])
                summary = b["summary"].get(lang, b["summary"]["en"])
                tags_html = " ".join(
                    f"<span class='status-badge warning' style='margin-right: 4px;'>{tag}</span>"
                    for tag in b["tags"]
                )

                st.markdown(f"""
                <div class="fazena-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-family: var(--fz-font-heading); font-size: 0.9rem;
                             color: var(--fz-text); letter-spacing: 1px; text-transform: uppercase;">
                            {title}
                        </div>
                        <span class="status-badge success">{b['year']}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: var(--fz-text-muted); line-height: 1.6;
                         margin-top: 0.75rem;">
                        {summary}
                    </div>
                    <div style="margin-top: 0.75rem;">{tags_html}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"📖 {t('l10_read_more')}", key=f"read_{i}"):
                    st.session_state["l10_article_idx"] = i
                    st.rerun()

        # Ask Gemma about news
        with st.expander("🤖 Discuss with Gemma"):
            question = st.text_input("Ask about breakthroughs:", key="l10_news_q",
                                      placeholder="What does AlphaFold 3 mean for drug design?")
            if st.button("Ask Gemma", key="l10_news_ask"):
                engine = get_gemma_engine()
                news_context = "; ".join(
                    b["title"]["en"] + ": " + b["summary"]["en"] for b in _BREAKTHROUGHS[:3]
                )
                response = engine.chat(
                    question,
                    difficulty=diff, language=lang,
                    context=f"Open World — discussing latest breakthroughs: {news_context}"
                )
                render_gemma_message(response)

    with tab_search:
        st.markdown(
            "<p style='color: var(--fz-text-muted); font-size: 0.85rem;'>"
            "Search for compounds in PubChem by name or SMILES. "
            "Gemma will help explain what you find.</p>",
            unsafe_allow_html=True
        )

        search_type = st.radio("Search by:", ["Name", "SMILES"], horizontal=True, key="l10_search_type")
        query = st.text_input(t("l10_search"), key="l10_search_input",
                               placeholder="aspirin, caffeine, CC(=O)O...")

        if st.button("Search PubChem", key="l10_search_btn", type="primary"):
            if query:
                import requests

                try:
                    if search_type == "Name":
                        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{query}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,XLogP/JSON"
                    else:
                        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{query}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,XLogP/JSON"

                    with st.spinner("Searching PubChem..."):
                        resp = requests.get(url, timeout=10)

                    if resp.status_code == 200:
                        data = resp.json()
                        props = data["PropertyTable"]["Properties"][0]

                        c1, c2 = st.columns(2)
                        with c1:
                            render_metric_card("Formula", props.get("MolecularFormula", "?"), "🧪")
                        with c2:
                            render_metric_card("MW", f"{props.get('MolecularWeight', '?')} g/mol", "⚖️")

                        st.markdown(f"""
                        <div class="fazena-card">
                            <div style="font-family: var(--fz-font-heading); font-size: 0.85rem;
                                 color: var(--fz-accent); letter-spacing: 1px; margin-bottom: 0.5rem;">
                                {props.get('IUPACName', 'Unknown')}</div>
                            <div style="font-family: var(--fz-font-mono); font-size: 0.8rem;
                                 color: var(--fz-text-muted);">
                                SMILES: {props.get('CanonicalSMILES', '?')}</div>
                            <div style="font-size: 0.8rem; color: var(--fz-text-dim);
                                 margin-top: 0.5rem;">
                                XLogP: {props.get('XLogP', '?')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Gemma explains
                        engine = get_gemma_engine()
                        response = engine.chat(
                            f"Tell me about the compound {query}: "
                            f"IUPAC: {props.get('IUPACName')}, {props.get('MolecularFormula')}, "
                            f"MW: {props.get('MolecularWeight')}, XLogP: {props.get('XLogP')}. "
                            f"What is it used for? Any known drug applications?",
                            difficulty=diff, language=lang,
                            context="Open World — PubChem compound exploration"
                        )
                        render_gemma_message(response)

                        # Save to research notes
                        if "research_notes" not in st.session_state:
                            st.session_state["research_notes"] = []
                        st.session_state["research_notes"].append({
                            "query": query,
                            "formula": props.get("MolecularFormula"),
                            "smiles": props.get("CanonicalSMILES"),
                            "mw": props.get("MolecularWeight"),
                        })
                    else:
                        st.warning(f"Compound not found: {query}")

                except Exception as e:
                    st.error(f"Search error: {str(e)[:200]}")

    with tab_report:
        st.markdown(
            "<p style='color: var(--fz-text-muted); font-size: 0.85rem;'>"
            "Generate a research report summarizing all your discoveries throughout FAZENIUM.</p>",
            unsafe_allow_html=True
        )

        notes = st.session_state.get("research_notes", [])
        fp = st.session_state.get("fazena_points", 0)
        name = st.session_state.get("scientist_name", "Researcher")

        st.markdown(f"""
        <div class="fazena-card">
            <div style="font-family: var(--fz-font-heading); font-size: 1rem;
                 color: var(--fz-accent); letter-spacing: 1.5px; text-transform: uppercase;
                 margin-bottom: 1rem;">Research Summary</div>
            <div style="color: var(--fz-text-muted); font-size: 0.85rem; line-height: 1.8;">
                <b>Scientist:</b> {name}<br>
                <b>Fazena Points:</b> {fp}<br>
                <b>Compounds Discovered:</b> {len(notes)}<br>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if notes:
            import pandas as pd
            df = pd.DataFrame(notes)
            st.dataframe(df, width="stretch", hide_index=True)

        if st.button(t("l10_export"), key="l10_export_btn", type="primary"):
            report_lines = [
                f"# FAZENIUM Research Report",
                f"## Scientist: {name}",
                f"## Fazena Points: {fp}",
                f"",
                f"### Compounds Explored",
            ]
            for note in notes:
                report_lines.append(f"- **{note['query']}**: {note.get('formula', '?')} | {note.get('smiles', '?')}")

            report_text = "\n".join(report_lines)
            st.download_button(
                "📥 Download Report (.md)",
                data=report_text,
                file_name="fazenium_report.md",
                mime="text/markdown",
                key="l10_download"
            )

            if "l10_exported" not in st.session_state:
                st.session_state["l10_exported"] = True
                st.session_state["fazena_points"] = st.session_state.get("fazena_points", 0) + 200
                st.toast("🌍 +200 FP for completing Open World!", icon="⚡")

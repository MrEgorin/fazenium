"""
FAZENIUM — EdTech Sandbox for Drug Design
Powered by Gemma 4 · Made by FAZENA
Main Streamlit Application
"""
import os
import sys
import streamlit as st

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import LEVELS, RANKS, LANGUAGES, DEFAULT_LANGUAGE, DEFAULT_DIFFICULTY
from modules.ui_components import (
    inject_custom_css, render_section_divider, render_footer,
    render_level_card, render_profile_panel, render_gemma_message,
    render_metric_card
)
from modules.localization import t
from modules.gemma_engine import get_gemma_engine


# ═══════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════
st.set_page_config(
    page_title="FAZENIUM — Drug Design Sandbox",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()


# ═══════════════════════════════════════════════════════
#  SESSION STATE INIT
# ═══════════════════════════════════════════════════════
_DEFAULTS = {
    "language": DEFAULT_LANGUAGE,
    "difficulty": DEFAULT_DIFFICULTY,
    "onboarded": False,
    "scientist_name": "",
    "scientist_avatar": "🧑‍🔬",
    "fazena_points": 0,
    "current_page": "dashboard",
    "gemma_chat_history": [],
}
for key, val in _DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val


def _get_rank():
    """Get current rank based on Fazena Points."""
    fp = st.session_state["fazena_points"]
    current_rank = RANKS[0]
    for rank in RANKS:
        if fp >= rank["min_fp"]:
            current_rank = rank
    return current_rank


# ═══════════════════════════════════════════════════════
#  ONBOARDING SCREEN
# ═══════════════════════════════════════════════════════
def _render_onboarding():
    """First-time setup: language, name, avatar."""
    st.markdown("<div class='onboarding-container'>", unsafe_allow_html=True)

    st.markdown(f"<div class='onboarding-title'>FAZENIUM</div>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color: var(--fz-text-muted); font-size: 0.95rem; line-height: 1.7; "
        f"max-width: 450px; margin: 0 auto 2rem;'>{t('welcome_message')}</p>",
        unsafe_allow_html=True
    )

    # Language
    col_lang, col_diff = st.columns(2)
    with col_lang:
        lang_options = list(LANGUAGES.values())
        lang_keys = list(LANGUAGES.keys())
        selected = st.selectbox(
            t("select_language"),
            lang_options,
            index=lang_keys.index(st.session_state["language"]),
            key="onboard_lang"
        )
        st.session_state["language"] = lang_keys[lang_options.index(selected)]

    with col_diff:
        diff_options = [t("difficulty_kid"), t("difficulty_student"), t("difficulty_expert")]
        diff_keys = ["kid", "student", "expert"]
        sel_diff = st.selectbox(
            t("select_difficulty"),
            diff_options,
            index=diff_keys.index(st.session_state["difficulty"]),
            key="onboard_diff"
        )
        st.session_state["difficulty"] = diff_keys[diff_options.index(sel_diff)]

    # Name
    name = st.text_input(
        t("enter_name"),
        placeholder=t("name_placeholder"),
        key="onboard_name"
    )

    # Avatar selection
    st.markdown(f"<p style='color: var(--fz-text-muted); margin-top: 1rem;'>{t('choose_avatar')}</p>",
                unsafe_allow_html=True)
    avatars = ["🧑‍🔬", "👩‍🔬", "👨‍🔬", "🧬", "⚗️", "🔬", "💊", "🧪"]
    cols = st.columns(len(avatars))
    for i, avatar in enumerate(avatars):
        with cols[i]:
            if st.button(avatar, key=f"avatar_{i}"):
                st.session_state["scientist_avatar"] = avatar

    sel_avatar = st.session_state["scientist_avatar"]
    st.markdown(
        f"<div style='text-align: center; font-size: 3rem; margin: 1rem 0;'>{sel_avatar}</div>",
        unsafe_allow_html=True
    )

    # Start
    if st.button(t("start_journey"), key="start_btn", type="primary"):
        if name.strip():
            st.session_state["scientist_name"] = name.strip()
            st.session_state["onboarded"] = True
            st.rerun()
        else:
            st.warning("Please enter your scientist name!")

    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════
def _render_sidebar():
    """Render the sidebar with profile, navigation, and settings."""
    with st.sidebar:
        # Logo area
        st.markdown("<div class='sidebar-logo-area'>", unsafe_allow_html=True)
        st.markdown(
            "<h2 style='font-family: var(--fz-font-heading); color: var(--fz-accent); "
            "font-size: 1.4rem; margin-bottom: 2px; border: none; padding: 0 !important; "
            "letter-spacing: 3px;'>FAZENIUM</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='color: var(--fz-text-dim); font-size: 0.65rem; margin-top: 0; "
            "letter-spacing: 2px; font-family: var(--fz-font-body); text-transform: uppercase;'>"
            "Drug Design Sandbox</p>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")

        # Profile panel
        rank = _get_rank()
        rank_name = t(rank["name_key"])
        render_profile_panel(
            st.session_state["scientist_avatar"],
            st.session_state["scientist_name"],
            f"{rank['badge']} {rank_name}",
            st.session_state["fazena_points"]
        )

        st.markdown("---")

        # Language & Difficulty
        col_l, col_d = st.columns(2)
        with col_l:
            lang_options = list(LANGUAGES.values())
            lang_keys = list(LANGUAGES.keys())
            cur_idx = lang_keys.index(st.session_state["language"])
            sel_lang = st.selectbox(
                t("select_language"), lang_options, index=cur_idx,
                key="sidebar_lang", label_visibility="collapsed"
            )
            st.session_state["language"] = lang_keys[lang_options.index(sel_lang)]

        with col_d:
            diff_map = {"kid": "🧒", "student": "🎓", "expert": "🧑‍🔬"}
            diff_keys = ["kid", "student", "expert"]
            sel_d = st.selectbox(
                t("select_difficulty"),
                diff_keys,
                index=diff_keys.index(st.session_state["difficulty"]),
                format_func=lambda x: f"{diff_map[x]} {x.title()}",
                key="sidebar_diff",
                label_visibility="collapsed"
            )
            st.session_state["difficulty"] = sel_d

        st.markdown("---")

        # Navigation
        st.markdown(
            f"<p style='color: var(--fz-text-dim); font-size: 0.7rem; letter-spacing: 1.5px; "
            f"text-transform: uppercase; font-family: var(--fz-font-body);'>{t('level_select')}</p>",
            unsafe_allow_html=True
        )

        # Dashboard button
        if st.button(f"🏠 {t('dashboard')}", key="nav_dash", use_container_width=True):
            st.session_state["current_page"] = "dashboard"
            st.rerun()

        # Level buttons
        for num, info in LEVELS.items():
            title = t(info["title_key"])
            btn_label = f"{info['icon']} L{num}: {title}"
            if st.button(btn_label, key=f"nav_l{num}", use_container_width=True):
                st.session_state["current_page"] = f"level_{num}"
                st.rerun()

        st.markdown("---")

        # Version badge
        st.markdown(
            "<div style='padding: 0.5rem 0;'>"
            "<span class='version-badge'>FAZENIUM v1.0</span>"
            "<p style='color: var(--fz-text-dim); font-size: 0.7rem; margin-top: 8px; "
            "font-family: var(--fz-font-body); line-height: 1.6;'>"
            "Developer: <span style='color: var(--fz-accent);'>FAZENA</span><br>"
            "<a href='https://www.fazena.org' style='color: var(--fz-accent); text-decoration: none;'>"
            "www.fazena.org</a></p></div>",
            unsafe_allow_html=True
        )


# ═══════════════════════════════════════════════════════
#  DASHBOARD (LAB HUB)
# ═══════════════════════════════════════════════════════
def _render_dashboard():
    """Main Lab Hub dashboard."""
    st.markdown(f"<h1 class='hero-title'>FAZENIUM</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color: var(--fz-text-muted); font-size: 1.05rem; margin-bottom: 0.5rem; "
        f"line-height: 1.7;'>{t('dash_hero_sub')}</p>",
        unsafe_allow_html=True
    )

    render_section_divider()

    # Progress overview
    st.markdown(f"<h2>{t('dash_progress')}</h2>", unsafe_allow_html=True)

    rank = _get_rank()
    fp = st.session_state["fazena_points"]

    # Find next rank
    current_idx = RANKS.index(rank)
    if current_idx < len(RANKS) - 1:
        next_rank = RANKS[current_idx + 1]
        progress = min(1.0, (fp - rank["min_fp"]) / (next_rank["min_fp"] - rank["min_fp"]))
        next_name = t(next_rank["name_key"])
    else:
        progress = 1.0
        next_name = "MAX"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card(t("rank_label"), f"{rank['badge']} {t(rank['name_key'])}", "🏅")
    with c2:
        render_metric_card(t("points_label"), str(fp), "⚡")
    with c3:
        render_metric_card("Next Rank", next_name, "🎯")
    with c4:
        render_metric_card("Progress", f"{progress * 100:.0f}%", "📊")

    st.progress(progress)

    render_section_divider()

    # Level grid
    st.markdown(f"<h2>{t('dash_modules')}</h2>", unsafe_allow_html=True)

    # 2-column grid for levels
    level_items = list(LEVELS.items())
    for row_start in range(0, len(level_items), 2):
        cols = st.columns(2)
        for col_idx in range(2):
            idx = row_start + col_idx
            if idx < len(level_items):
                num, info = level_items[idx]
                with cols[col_idx]:
                    title = t(info["title_key"])
                    desc_key = info["title_key"].replace("_title", "_desc")
                    desc = t(desc_key)
                    render_level_card(info["icon"], f"L{num}: {title}", desc, info["fp_reward"])

                    if st.button(f"Enter L{num}", key=f"dash_enter_{num}",
                                  use_container_width=True):
                        st.session_state["current_page"] = f"level_{num}"
                        st.rerun()

    render_section_divider()

    # Gemma Console on dashboard
    _render_gemma_console()

    render_footer()


# ═══════════════════════════════════════════════════════
#  GEMMA CONSOLE
# ═══════════════════════════════════════════════════════
def _render_gemma_console():
    """Persistent Gemma chat console."""
    st.markdown("""
    <div class="gemma-console">
        <div class="gemma-console-header">
            <div class="gemma-dot"></div>
            """ + t("gemma_title") + """
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Chat history
    for msg in st.session_state["gemma_chat_history"]:
        render_gemma_message(msg["content"], msg["role"])

    # Input
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_msg = st.text_input(
            t("gemma_placeholder"),
            key="gemma_input",
            label_visibility="collapsed",
            placeholder=t("gemma_placeholder")
        )
    with col_btn:
        send = st.button(t("gemma_send"), key="gemma_send_btn")

    if send and user_msg:
        st.session_state["gemma_chat_history"].append({"role": "user", "content": user_msg})
        
        # We need a temporary AI message to stream into
        with st.chat_message("assistant", avatar="✨"):
            placeholder = st.empty()
            full_response = ""
            engine = get_gemma_engine()
            for chunk in engine.stream_chat(
                user_msg,
                difficulty=st.session_state["difficulty"],
                language=st.session_state["language"],
                context="General FAZENIUM chat"
            ):
                full_response += chunk
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
            
        st.session_state["gemma_chat_history"].append({"role": "ai", "content": full_response})
        st.rerun()


# ═══════════════════════════════════════════════════════
#  AI LEVEL GUIDE
# ═══════════════════════════════════════════════════════
def _render_level_ai_guide(level_num: int):
    """Render an AI-generated briefing and Q&A before the level."""
    from config import LEVELS
    title = t(LEVELS[level_num]["title_key"])
    
    st.markdown("---")
    with st.expander(f"🤖 {t('gemma_title')}: {title}", expanded=False):
        engine = get_gemma_engine()
        lang = st.session_state["language"]
        diff = st.session_state["difficulty"]
        
        # We cache the briefing in session state to avoid regenerating on every UI refresh
        cache_key = f"ai_briefing_{level_num}_{lang}_{diff}"
        
        guide_placeholder = st.empty()
        
        if cache_key not in st.session_state:
            with guide_placeholder.container():
                st.markdown(f"*{t('gemma_thinking')}*")
                full_briefing = ""
                for chunk in engine.stream_chat(
                    f"Generate a short mission briefing for Level {level_num}: {title}. 2-3 sentences.",
                    difficulty=diff, language=lang
                ):
                    full_briefing += chunk
                    guide_placeholder.markdown(
                        f"<div style='font-size:0.95rem; line-height:1.6; color: var(--fz-text);'>{full_briefing}</div>",
                        unsafe_allow_html=True
                    )
                st.session_state[cache_key] = full_briefing
        else:
            guide_placeholder.markdown(
                f"<div style='font-size:0.95rem; line-height:1.6; color: var(--fz-text);'>{st.session_state[cache_key]}</div>",
                unsafe_allow_html=True
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        q_key = f"guide_q_{level_num}"
        question = st.text_input(t("gemma_placeholder"), key=q_key, label_visibility="collapsed", placeholder=t("gemma_placeholder"))
        
        if st.button(t("gemma_send"), key=f"guide_ask_{level_num}"):
            if question:
                ans_placeholder = st.empty()
                full_ans = ""
                for chunk in engine.stream_chat(
                    question,
                    difficulty=diff,
                    language=lang,
                    context=f"Discussion of Level: {title}"
                ):
                    full_ans += chunk
                    ans_placeholder.markdown(f"<div class='gemma-msg ai'>{full_ans}</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
#  LEVEL ROUTING
# ═══════════════════════════════════════════════════════
def _render_level(level_num: int):
    """Route to the appropriate level module."""
    try:
        if level_num == 1:
            from levels.level_01_life_code import render_level
            render_level()
        elif level_num == 2:
            from levels.level_02_molecular_origami import render_level
            render_level()
        elif level_num in (3, 4, 5):
            from levels.level_03_3d_labyrinth import render_level
            render_level(sub_level=level_num)
        elif level_num == 6:
            from levels.level_06_keyhole import render_level
            render_level()
        elif level_num in (7, 8):
            from levels.level_07_constructor import render_level
            render_level(sub_level=level_num)
        elif level_num == 9:
            from levels.level_09_stress_test import render_level
            render_level()
        elif level_num == 10:
            from levels.level_10_open_world import render_level
            render_level()

        # Render AI guide AFTER level content for better performance perception
        _render_level_ai_guide(level_num)

        # Gemma console at the bottom of every level
        render_section_divider()
        _render_gemma_console()
        render_footer()

    except Exception as e:
        st.error(f"Error loading level {level_num}: {e}")
        import traceback
        st.code(traceback.format_exc())


# ═══════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════
def main():
    if not st.session_state["onboarded"]:
        _render_onboarding()
        return

    _render_sidebar()

    page = st.session_state["current_page"]

    if page == "dashboard":
        _render_dashboard()
    elif page.startswith("level_"):
        level_num = int(page.split("_")[1])
        _render_level(level_num)
    else:
        _render_dashboard()


if __name__ == "__main__":
    main()

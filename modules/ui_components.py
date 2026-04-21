"""
FAZENIUM — Design System & UI Components
Adapted from Fazena.org — Dark mode, Glassmorphism, Neon Cyan/Green accents
"""
import streamlit as st


def inject_custom_css():
    st.markdown("""
    <style>
    /* ═══════════════════════════════════════════════════════════
       FAZENIUM Design System
       Theme: Futuristic Scientific Laboratory
       ═══════════════════════════════════════════════════════════ */

    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Audiowide&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Design Tokens ── */
    :root {
        --fz-bg-primary:    #070709;
        --fz-bg-secondary:  #0D0D12;
        --fz-bg-card:       rgba(18, 18, 24, 0.7);
        --fz-bg-card-hover: rgba(25, 25, 35, 0.85);
        --fz-accent:        #00F0FF;
        --fz-accent-dim:    #00b8c4;
        --fz-accent-alt:    #39FF14;
        --fz-accent-glow:   rgba(0, 240, 255, 0.4);
        --fz-accent-glow-s: rgba(0, 240, 255, 0.1);
        --fz-accent-alt-glow: rgba(57, 255, 20, 0.2);
        --fz-text:          #FFFFFF;
        --fz-text-muted:    rgba(255, 255, 255, 0.65);
        --fz-text-dim:      rgba(255, 255, 255, 0.4);
        --fz-border:        rgba(0, 240, 255, 0.12);
        --fz-border-hover:  rgba(0, 240, 255, 0.3);
        --fz-radius-card:   20px;
        --fz-radius-btn:    10px;
        --fz-radius-input:  10px;
        --fz-font-heading:  'Audiowide', sans-serif;
        --fz-font-body:     'Inter', sans-serif;
        --fz-font-mono:     'JetBrains Mono', monospace;
    }

    /* ── App Background ── */
    .stApp {
        background: var(--fz-bg-primary) !important;
        background-image: 
            radial-gradient(circle at 50% -20%, rgba(0, 240, 255, 0.12), transparent 70%),
            radial-gradient(circle at 0% 100%, rgba(57, 255, 20, 0.08), transparent 50%),
            radial-gradient(circle at 100% 100%, rgba(0, 240, 255, 0.08), transparent 50%) !important;
        color: var(--fz-text);
        font-family: var(--fz-font-body);
    }
    
    /* Subtle animated grid background */
    .stApp::before {
        content: ""; position: fixed; inset: 0;
        background-image: linear-gradient(rgba(0, 240, 255, 0.04) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(0, 240, 255, 0.04) 1px, transparent 1px);
        background-size: 60px 60px;
        z-index: -1; pointer-events: none;
        opacity: 0.5;
    }

    /* ── Typography ── */
    h1, h2, h3 {
        font-family: var(--fz-font-heading) !important;
        letter-spacing: 2px !important;
        text-transform: uppercase;
        background: linear-gradient(90deg, #fff, var(--fz-accent));
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    h1 { font-size: 2.2rem !important; margin-bottom: 1rem !important; }
    
    /* ── Glass Cards ── */
    .fazena-card {
        background: var(--fz-bg-card);
        border: 1px solid var(--fz-border);
        border-radius: var(--fz-radius-card);
        padding: 2rem;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        margin-bottom: 1.5rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .fazena-card:hover {
        transform: translateY(-5px);
        border-color: var(--fz-accent-glow);
        box-shadow: 0 15px 45px rgba(0, 0, 0, 0.6), 0 0 20px var(--fz-accent-glow-s);
    }

    /* ── Level Cards ── */
    .level-card {
        background: var(--fz-bg-card);
        border: 1px solid var(--fz-border);
        border-radius: var(--fz-radius-card);
        padding: 1.5rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer; position: relative;
    }
    .level-card:hover {
        border-color: var(--fz-accent);
        box-shadow: 0 0 30px var(--fz-accent-glow), 0 10px 30px rgba(0,0,0,0.5);
        transform: scale(1.02);
    }
    .level-card .level-icon { font-size: 2.5rem; margin-bottom: 0.5rem; filter: drop-shadow(0 0 8px var(--fz-accent-glow)); }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.1), transparent) !important;
        border: 1px solid var(--fz-accent) !important;
        border-radius: var(--fz-radius-btn) !important;
        color: var(--fz-accent) !important;
        font-family: var(--fz-font-heading) !important;
        text-transform: uppercase; letter-spacing: 2px;
        padding: 0.8rem 2rem !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: var(--fz-accent) !important;
        color: #000 !important;
        box-shadow: 0 0 25px var(--fz-accent-glow) !important;
        transform: translateY(-2px);
    }

    /* ── Chat bubbles ── */
    .gemma-msg {
        padding: 1rem 1.25rem; border-radius: 15px; margin-bottom: 1rem;
        font-size: 0.9rem; line-height: 1.6;
    }
    .gemma-msg.ai {
        background: rgba(0, 240, 255, 0.08);
        border-left: 4px solid var(--fz-accent);
        color: var(--fz-text);
    }
    .gemma-msg.user {
        background: rgba(255, 255, 255, 0.05);
        border-right: 4px solid var(--fz-text-muted);
        text-align: right;
    }

    /* ── Metric Cards ── */
    div[data-testid="stMetric"] {
        background: var(--fz-bg-card) !important;
        border: 1px solid var(--fz-border) !important;
        border-radius: var(--fz-radius-card) !important;
        padding: 1.25rem !important;
        box-shadow: inset 0 0 10px rgba(0, 240, 255, 0.05) !important;
    }

    /* ── Animations ── */
    @keyframes scan {
        0% { transform: translateY(-100%); }
        100% { transform: translateY(1000%); }
    }
    .scan-line {
        position: absolute; width: 100%; height: 2px;
        background: linear-gradient(90deg, transparent, var(--fz-accent), transparent);
        opacity: 0.3; animation: scan 8s linear infinite;
    }
    
    /* ── Sequence Display ── */
    .nt-A { color: #FF6B6B; font-weight: bold; }
    .nt-T, .nt-U { color: #4ECDC4; font-weight: bold; }
    .nt-G { color: #FFE66D; font-weight: bold; }
    .nt-C { color: #A78BFA; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)


def render_section_divider():
    st.markdown("<hr style='border: none; height: 1px; background: linear-gradient(90deg, transparent, var(--fz-border), transparent); margin: 2.5rem 0;'>", unsafe_allow_html=True)


def render_metric_card(label: str, value: str, icon: str = ""):
    st.markdown(f"""
    <div style="background: var(--fz-bg-card); border: 1px solid var(--fz-border);
                border-radius: 20px; padding: 1.5rem; text-align: center;
                backdrop-filter: blur(10px);">
        <div style="font-size: 2rem; margin-bottom: 0.5rem; filter: drop-shadow(0 0 10px var(--fz-accent-glow));">{icon}</div>
        <div style="font-family: var(--fz-font-heading); font-size: 1.6rem;
                    color: var(--fz-accent); margin-bottom: 0.3rem;
                    text-shadow: 0 0 15px var(--fz-accent-glow);">{value}</div>
        <div style="font-family: var(--fz-font-body); font-size: 0.8rem;
                    color: var(--fz-text-muted); letter-spacing: 1.5px;
                    text-transform: uppercase;">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_gemma_message(content: str, role: str = "ai"):
    st.markdown(f"<div class='gemma-msg {role}'>{content}</div>", unsafe_allow_html=True)


def render_level_card(icon: str, title: str, desc: str, fp: int, locked: bool = False):
    lock_cls = " locked" if locked else ""
    st.markdown(f"""
    <div class="level-card{lock_cls}">
        <div class="level-icon">{icon}</div>
        <div class="level-title">{title}</div>
        <div class="level-desc">{desc}</div>
        <div class="level-fp">⚡ +{fp} FP</div>
    </div>
    """, unsafe_allow_html=True)


def render_profile_panel(avatar: str, name: str, rank: str, fp: int):
    st.markdown(f"""
    <div class="profile-panel" style="background: var(--fz-bg-card); border: 1px solid var(--fz-border);
                                      border-radius: 20px; padding: 1.5rem; text-align: center;
                                      backdrop-filter: blur(15px); margin-bottom: 1rem;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem; filter: drop-shadow(0 0 15px var(--fz-accent-glow));">{avatar}</div>
        <div style="font-family: var(--fz-font-heading); font-size: 1.1rem; color: var(--fz-accent);
                    letter-spacing: 2px; text-transform: uppercase;">{name}</div>
        <div style="font-size: 0.8rem; color: var(--fz-text-muted); margin-top: 4px;">{rank}</div>
        <div style="font-family: var(--fz-font-mono); font-size: 1rem; color: var(--fz-accent-alt);
                    margin-top: 12px; font-weight: bold;">{fp} FP</div>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    st.markdown(
        "<div style='text-align: center; padding: 3rem 0 1rem; color: var(--fz-text-dim); font-size: 0.75rem; letter-spacing: 2px;'>"
        "SYSTEM_FAZENIUM // BUILD_2026 // <a href='https://www.fazena.org' style='color:var(--fz-accent); text-decoration:none;'>FAZENA.ORG</a>"
        "</div>",
        unsafe_allow_html=True
    )


def colorize_sequence(seq: str) -> str:
    """Return HTML with colored nucleotide/amino acid letters."""
    out = []
    for ch in seq.upper():
        if ch in "ATUGC":
            out.append(f"<span class='nt-{ch}'>{ch}</span>")
        else:
            out.append(f"<span style='color: var(--fz-text-dim);'>{ch}</span>")
    return "".join(out)

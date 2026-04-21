"""
FAZENIUM — Global Configuration & Constants
"""
import os

# ─── Paths ───────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")

# ─── LLM Configuration ───────────────────────────────
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "gemma4:e2b"
GEMINI_API_KEY = "AIzaSyCx4ZtuDUCJns2D9m3lIZngJQJ9NNvGWZY"
GEMINI_MODEL = "gemma-4-26b-a4b-it"
HF_API_MODEL = "google/gemma-2-2b-it" # Fallback or reference

# ─── Level Definitions ───────────────────────────────
LEVELS = {
    1:  {"key": "life_code",       "title_key": "level_1_title",  "icon": "🧬", "fp_reward": 100},
    2:  {"key": "molecular_origami","title_key": "level_2_title", "icon": "🔬", "fp_reward": 150},
    3:  {"key": "structure_voyage", "title_key": "level_3_title",  "icon": "🏗️", "fp_reward": 200},
    4:  {"key": "dual_horizon",     "title_key": "level_4_title",  "icon": "🔍", "fp_reward": 200},
    5:  {"key": "pattern_master",   "title_key": "level_5_title",  "icon": "🧩", "fp_reward": 250},
    6:  {"key": "active_site_bio",  "title_key": "level_6_title",  "icon": "🔑", "fp_reward": 300},
    7:  {"key": "molecular_forge",  "title_key": "level_7_title",  "icon": "⚗️", "fp_reward": 350},
    8:  {"key": "clinical_architect","title_key": "level_8_title",  "icon": "💊", "fp_reward": 400},
    9:  {"key": "dynamic_frontier", "title_key": "level_9_title",  "icon": "⚡", "fp_reward": 500},
    10: {"key": "global_nexus",     "title_key": "level_10_title", "icon": "🌍", "fp_reward": 1000},
}

# ─── RPG Ranks ────────────────────────────────────────
RANKS = [
    {"name_key": "rank_junior",      "min_fp": 0,    "badge": "🔰"},
    {"name_key": "rank_researcher",  "min_fp": 500,  "badge": "🔬"},
    {"name_key": "rank_engineer",    "min_fp": 1500, "badge": "⚙️"},
    {"name_key": "rank_senior",      "min_fp": 3000, "badge": "🏆"},
    {"name_key": "rank_head",        "min_fp": 5000, "badge": "👑"},
]

# ─── Difficulty Profiles ──────────────────────────────
DIFFICULTY_PROFILES = {
    "kid":     {"system_note": "Explain like to a curious 10-year-old. Use analogies, fun comparisons, and emojis."},
    "student": {"system_note": "Explain at university biochemistry level. Use proper terminology but stay accessible."},
    "expert":  {"system_note": "Respond at PhD-level. Use precise scientific language, cite mechanisms and papers."},
}

# ─── Supported Languages ─────────────────────────────
LANGUAGES = {
    "en": "English",
    "ua": "Українська",
    "de": "Deutsch",
}

DEFAULT_LANGUAGE = "en"
DEFAULT_DIFFICULTY = "student"

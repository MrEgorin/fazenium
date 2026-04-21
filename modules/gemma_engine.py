"""
FAZENIUM — Gemma Engine (Google Gemini API Exclusive)
High-performance cloud-based intelligence using Gemma 4 via Gemini API.
"""
import os
import streamlit as st
from config import GEMINI_API_KEY, GEMINI_MODEL, DIFFICULTY_PROFILES


# ─── API Error Responses ───────────────────────────
_ERROR_RESPONSES = {
    "en": "⚠️ Gemini API Error. Please check your internet connection or API key in config.py.",
    "ua": "⚠️ Помилка Gemini API. Будь ласка, перевірте з'єднання або API-ключ у config.py.",
    "de": "⚠️ Gemini-API-Fehler. Bitte überprüfen Sie Ihre Internetverbindung oder Ihren API-Schlüssel.",
}


class GemmaEngine:
    """Wrapper around Google Gemini API for Gemma 4."""

    def __init__(self):
        self._client = None
        self._available = False
        
    def initialize(self) -> bool:
        """Initialize the Gemini API client."""
        if self._available:
            return True

        if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_KEY":
            st.error("🔑 Missing GEMINI_API_KEY in config.py!")
            return False

        try:
            from google import genai
            self._client = genai.Client(api_key=GEMINI_API_KEY)
            self._available = True
            return True
        except ImportError:
            st.error("📦 Missing package: 'google-genai'. Run: pip install google-genai")
            return False
        except Exception as e:
            st.error(f"❌ Gemini Initialization Error: {e}")
            return False

    def _build_system_prompt(self, difficulty: str, language: str, context: str = "") -> str:
        """Build a system prompt based on difficulty and language."""
        profile = DIFFICULTY_PROFILES.get(difficulty, DIFFICULTY_PROFILES["student"])
        lang_map = {"en": "English", "ua": "Ukrainian", "de": "German"}
        lang_name = lang_map.get(language, "English")

        prompt = (
            f"You are FAZENIUM AI — a friendly, knowledgeable tutor in drug design and biochemistry. "
            f"You are part of the FAZENIUM game by FAZENA. "
            f"{profile['system_note']} "
            f"Always respond in {lang_name}. "
            f"Be encouraging, use relevant emojis occasionally. "
            f"Keep responses concise but informative (2-4 paragraphs max)."
        )
        if context:
            prompt += f"\n\nCurrent context: {context}"
        return prompt

    def stream_chat(self, user_message: str, difficulty: str = "student",
                    language: str = "en", context: str = ""):
        """Stream a response via Gemini API."""
        if not self._available:
            if not self.initialize():
                yield _ERROR_RESPONSES.get(language, _ERROR_RESPONSES["en"])
                return

        system_prompt = self._build_system_prompt(difficulty, language, context)

        try:
            # Using System Instruction + User Prompt
            # The google-genai SDK supports system_instruction parameter
            response = self._client.models.generate_content_stream(
                model=GEMINI_MODEL,
                contents=user_message,
                config={
                    "system_instruction": system_prompt,
                    "temperature": 0.7,
                    "max_output_tokens": 1000,
                }
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"⚠️ API Error: {str(e)[:200]}"

    def chat(self, user_message: str, difficulty: str = "student",
             language: str = "en", context: str = "") -> str:
        """Blocking chat call."""
        response = ""
        for chunk in self.stream_chat(user_message, difficulty, language, context):
            response += chunk
        return response if response else "..."

    # ─── High-level Helper Methods ───────────────────

    def get_tutor_response(self, topic: str, difficulty: str, language: str) -> str:
        return self.chat(f"Explain {topic} in drug design context.", difficulty, language)

    def get_narrator_briefing(self, level_name: str, difficulty: str, language: str) -> str:
        return self.chat(f"Generate a dramatic briefing for level: {level_name}. 2 sentences.", difficulty, language)

    def get_molecule_critique(self, smiles: str, properties: dict, difficulty: str, language: str) -> str:
        props_str = ", ".join(f"{k}: {v}" for k, v in properties.items())
        return self.chat(f"Analyze molecule SMILES: {smiles}. Props: {props_str}", difficulty, language)

    def query_target_database(self, target_name: str, difficulty: str, language: str) -> str:
        return self.chat(f"Analyze biological target: {target_name}", difficulty, language)

    def query_ligand_database(self, ligand_name: str, difficulty: str, language: str) -> str:
        return self.chat(f"Analyze ligand: {ligand_name}", difficulty, language)

    def get_sequence_analysis(self, seq_type: str, seq_preview: str, stats: dict, difficulty: str, language: str) -> str:
        return self.chat(f"Analyze {seq_type} sequence: {seq_preview}", difficulty, language)

    def shutdown(self):
        self._available = False


@st.cache_resource
def get_gemma_engine() -> GemmaEngine:
    engine = GemmaEngine()
    engine.initialize()
    return engine

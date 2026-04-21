# 🧬 FAZENIUM — AI-Powered Drug Design Sandbox

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Gemma 4](https://img.shields.io/badge/AI-Gemma%204-00F0FF.svg)](https://ai.google.dev/gemma)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)

> **"Democratizing Computational Biology through Gaming and Generative AI."**

**FAZENIUM** is an interactive, futuristic laboratory sandbox that teaches the fundamentals of drug discovery. Built for students and researchers, it integrates professional scientific tools with the reasoning power of **Google Gemma 4**.

---

## ✨ Key Features
- **10 Progressive Levels**: A full curriculum from genomic sequence analysis to 3D molecular docking.
- **Gemma 4 AI Tutor**: Real-time, context-aware scientific guidance powered by the Gemini API (`gemma-4-26b-a4b-it`).
- **Interactive 3D Visuals**: Explore proteins and ligands using a hardware-accelerated **3Dmol.js** viewer.
- **Scientific Fidelity**: Native integration with **RDKit**, **Biopython**, and custom Physics engines for Molecular Dynamics.
- **Premium Design**: A high-fidelity "Futuristic Lab" interface featuring dark-mode glassmorphism and neon-cyan aesthetics.

---

## 🚀 Tech Stack
- **Frontend/App**: Streamlit (Python)
- **AI Core**: Google Gemini API (Gemma 4)
- **Chemistry**: RDKit (Conformer generation & property analysis)
- **Bioinformatics**: Biopython (PDB/FASTA processing)
- **3D Visualization**: 3Dmol.js
- **Data Science**: Pandas, NumPy, Plotly

---

## 🛠️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/fazenium.git
   cd fazenium
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key**:
   Open `config.py` and add your Google Gemini API Key:
   ```python
   GEMINI_API_KEY = "YOUR_API_KEY_HERE"
   ```

4. **Launch the platform**:
   ```bash
   streamlit run app.py
   ```

---

## 📸 Screenshots
<img width="1761" height="994" alt="Снимок экрана 2026-04-21 215227" src="https://github.com/user-attachments/assets/65e9edfd-c07a-4060-a3f3-60c8283a02aa" />
<img width="1759" height="1262" alt="Снимок экрана 2026-04-21 215505" src="https://github.com/user-attachments/assets/f0d88d0a-0f8b-40db-b13d-7446ddbf023e" />
<img width="2290" height="1135" alt="Снимок экрана 2026-04-21 215325" src="https://github.com/user-attachments/assets/b9f617ad-841d-4bc5-8993-fb4e01e66789" />
<img width="1762" height="1233" alt="Снимок экрана 2026-04-21 215628" src="https://github.com/user-attachments/assets/bd046560-a4f6-4076-ae76-00f23b3f744e" />
<img width="1755" height="978" alt="Снимок экрана 2026-04-21 220014" src="https://github.com/user-attachments/assets/f03b4e5d-27a0-499c-a1bf-ecbbe1da5a00" />
<img width="1728" height="1225" alt="Снимок экрана 2026-04-21 220141" src="https://github.com/user-attachments/assets/7d5024f1-fdea-4748-921b-b226a4c19693" />
<img width="1456" height="720" alt="Gemini_Generated_Image_v4kqsyv4kqsyv4kq" src="https://github.com/user-attachments/assets/c8901142-6721-4c1e-9c3c-0eb8b2fea669" />

---

## 🎯 Why FAZENIUM?
The drug discovery pipeline is complex and inaccessible. FAZENIUM removes the barrier to entry by providing:
- **Instant Feedback**: No more waiting for server-side simulations; get AI insights in seconds.
- **Immersive Narrative**: Learn biochemistry by solving "missions," not just reading text.
- **Scientist-in-the-Loop**: Gemma 4 acts as a personal mentor, adapting its difficulty to your level.

---

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Built with 💙 by **FAZENA** for the Google Gemma Hackathon 2026.

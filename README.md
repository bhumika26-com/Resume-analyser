# AI Resume Analyzer (ATS Simulator)

A fully functional, AI-powered Streamlit web application that simulates an Applicant Tracking System. By uploading your resume and providing a job description, you can see how well your resume matches the job requirements, find missing keywords, and get tailored AI-driven suggestions on how to improve.

## Features Let’s Dive In

- **Resume Parsing**: Supports `.pdf` and `.docx` file formats.
- **ATS Match Scoring**: Calculates an ATS compatibility score (1-100%) using a combination of keyword extraction, TF-IDF cosine similarity, and structural completeness checks.
- **Deep Keyword Analysis**: Uses `spaCy` NLP to systematically find overlapping skills between the resume and job description.
- **Section Detection**: Scans for standard resume sections (Experience, Education, Skills, Projects).
- **Interactive UI**: Clean, responsive layout leveraging Streamlit and interactive Plotly gauges.
- **AI Feedback**: Direct integration with Google Gemini Pro API for actionable feedback (Strengths, Weaknesses, Suggestions).

---

## 🛠 Prerequisites

Make sure you have:
- Python 3.9+
- A Google Gemini API Key (get one from [Google AI Studio](https://aistudio.google.com/)).

---

## 📦 Setup Instructions

**1. Clone or Download the repository.**
Navigate to the root directory `resume-analyzer/`.

**2. Create a virtual environment.** (Highly Recommended)
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

**3. Install Dependencies.**
```bash
pip install -r requirements.txt
```

**4. Download the Core English NLP model (spaCy).**
*(The app will try to download this automatically if missing, but it is much safer to install manually beforehand)*
```bash
python -m spacy download en_core_web_sm
```

**5. (Optional) Set up your Gemini API Key.**
You can place your key directly inside a `.env` file at the root of `resume-analyzer/`:
```env
GEMINI_API_KEY=your_api_key_here
```
*(Alternatively, you can just paste the key directly into the app sidebar while it is running).*

---

## 🚀 Running the App

```bash
streamlit run app.py
```

- A local server will start on port `8501`.
- Your browser will automatically open: `http://localhost:8501`.
- Now, upload a resume and try it out!

---

## Architecture Overview

- **`app.py`**: The Streamlit entry point. Controls layout, state, and visual presentation.
- **`utils/parser.py`**: Handles all document binary parsing (PyPDF2 & python-docx).
- **`utils/analyzer.py`**: Houses `spaCy` logic for keyword extraction and section parsing.
- **`utils/scorer.py`**: Generates the TF-IDF statistical match metrics.
- **`utils/llm_helper.py`**: Wrapper for `google-generativeai` to request and parse structural JSON from the LLM.




#How to run
Navigate to the root directory `resume-analyzer/`.

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

python -m spacy download en_core_web_sm

streamlit run app.py
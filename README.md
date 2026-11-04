# 📄 ATS Resume Analyzer

A Streamlit app that scores your resume for Applicant Tracking Systems (ATS) and gives
specific, prioritized suggestions for improvement, powered by Google Gemini Flash.

## Features
- Upload a resume as **PDF, DOCX or TXT**
- Overall **ATS score (0-100)** with a breakdown: keywords, formatting, content quality, structure, readability
- Strengths, weaknesses and **missing keywords**
- Prioritized improvements (High / Medium / Low) with example fixes
- Optional **job description** input for role-specific scoring
- Download the report as Markdown

## Project structure
```
.
├── app.py
├── requirements.txt
└── README.md
```

## Run locally
1. Get a free Gemini API key at https://aistudio.google.com/apikey
2. Install and run:
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
3. Provide your API key in one of these ways:
   - Paste it in the app sidebar, or
   - Create `.streamlit/secrets.toml`:
     ```toml
     GEMINI_API_KEY = "your-key-here"
     # Optional: change the model
     # GEMINI_MODEL = "gemini-3.6-flash"
     ```
   - Or set an environment variable: `export GEMINI_API_KEY=your-key-here`

## Deploy on Streamlit Community Cloud
1. Push this repo to GitHub (never commit your API key).
2. Go to https://share.streamlit.io, click **Create app**, pick your repo, branch `main`, main file `app.py`.
3. Open **Advanced settings → Secrets** and add:
   ```toml
   GEMINI_API_KEY = "your-key-here"
   ```
4. Click **Deploy**.

## Configuration
| Setting | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | none | Your Gemini API key (secrets or env var) |
| `GEMINI_MODEL` | `gemini-3.6-flash` | Any Gemini Flash model ID |

## Limitations
- Scanned/image-only PDFs are not supported (no extractable text).
- The score is an AI estimate, not the output of a real ATS.
- Your resume text is sent to Google's Gemini API.

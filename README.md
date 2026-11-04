Resume ATS Analyzer
A Streamlit application that analyzes PDF, DOCX, and TXT resumes with Google's Gemini Flash model.
Features
- Estimated ATS-readiness score out of 100
- Optional job-description matching
- Strengths, issues, matched keywords, and potential keyword gaps
- Section feedback and prioritized improvement suggestions
- JSON report download
The score is an AI estimate, not a score from a real employer ATS or a hiring prediction.

Run locally
Use Python 3.10 or newer.
python -m venv .venv

# Windows PowerShell:
.venv\\Scripts\\Activate.ps1

# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
Get a Gemini API key from https://aistudio.google.com/app/apikey and enter it in the app sidebar.

You can alternatively set environment variables:
# macOS/Linux
export GEMINI_API_KEY="your-key"
export GEMINI_MODEL="gemini-2.5-flash"

# Windows PowerShell
$env:GEMINI_API_KEY="your-key"
$env:GEMINI_MODEL="gemini-2.5-flash"
Push to GitHub
Create an empty GitHub repository, then run in this project folder:
git init
git add app.py README.md requirements.txt
git commit -m "Initial Resume ATS Analyzer"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
Never commit your API key. A .gitignore file is recommended:
.venv/
__pycache__/
*.pyc
.env
.streamlit/secrets.toml
Deploy on Streamlit Community Cloud
1. Push the project to GitHub.
2. Visit https://share.streamlit.io/ and sign in with GitHub.
3. Create an app and select your repository, main branch, and app.py.
4. In the app settings, add these secrets:
GEMINI_API_KEY = "your-real-api-key"
GEMINI_MODEL = "gemini-2.5-flash"
5. Deploy. Streamlit installs packages from requirements.txt.
Notes and privacy
- Resume text is sent to Google's Gemini API for analysis.
- This starter app does not save uploaded files to a database.
- Scanned/image-only PDFs need OCR before upload.
- Complex columns and tables may not extract in reading order.
- Only add suggested keywords if they truthfully reflect your skills and experience.
- Do not upload resumes without the owner's permission.

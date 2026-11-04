Resume ATS Analyzer
A Streamlit app that accepts a resume (PDF, DOCX, or TXT) and uses Google's Gemini Flash model to estimate ATS readiness, compare the resume with an optional job description, identify relevant keyword gaps, and suggest improvements.
Important: The score is an AI-generated estimate. Different applicant tracking systems and employers use different parsing and ranking rules. This app cannot reproduce a real employer's ATS score or predict hiring outcomes.

Features
- PDF, DOCX, and TXT resume upload
- Optional job-description matching (recommended for a meaningful role-specific review)
- Estimated ATS-readiness score (0–100)
- Strengths, issues, matched and potentially missing keywords
- Section feedback, formatting tips, and prioritized suggestions
- JSON report download
- Gemini API key entered in the UI or provided through environment variables / Streamlit secrets
1. Requirements
- Python 3.10 or newer
- A Gemini API key from Google AI Studio
2. Run locally
# Create and activate a virtual environment
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

# Install packages
pip install -r requirements.txt

# Start the app
streamlit run app.py
Open the local URL printed by Streamlit (normally http://localhost:8501). Paste your Gemini API key into the sidebar.
Optional: use an environment variable
# macOS / Linux
export GEMINI_API_KEY="your-key"

# Windows PowerShell
$env:GEMINI_API_KEY="your-key"
You can also set GEMINI_MODEL to override the default model (gemini-2.5-flash).
3. Push to GitHub
Create an empty repository on GitHub, then run these commands from the project folder:
git init
git add app.py README.md requirements.txt
git commit -m "Initial resume ATS analyzer"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
Replace the remote URL with your own repository URL. If Git asks you to authenticate, use GitHub's supported sign-in flow or a personal access token; do not put a token in the repository.
Keep secrets out of Git
Never commit your Gemini API key. Add a .gitignore file before pushing if you create local secret/config files:
.venv/
__pycache__/
*.pyc
.env
.streamlit/secrets.toml
The .gitignore is recommended even though this starter project contains the three requested application files.
4. Deploy on Streamlit Community Cloud
1. Push the project to GitHub.
2. Sign in at Streamlit Community Cloud using GitHub.
3. Select Create app, choose your repository, branch (main), and main file path (app.py).
4. Open the app's Advanced settings / Secrets section.
5. Add your key in TOML format:
   GEMINI_API_KEY = "your-real-api-key"
   GEMINI_MODEL = "gemini-2.5-flash"
6. Deploy. Streamlit installs dependencies from requirements.txt.
7. Test with a non-sensitive sample resume and a relevant job description.
The app reads GEMINI_API_KEY and GEMINI_MODEL directly from Streamlit secrets when deployed, or from environment variables when running locally. You can still override the API key in the sidebar.
5. How to get better feedback
- Paste the exact job description for a role-specific analysis.
- Upload a text-based PDF or DOCX. Scanned/image-only PDFs are not OCR'd by this starter app.
- Keep the resume factual. Only add suggested keywords if you genuinely have that skill or experience.
- Use conventional headings such as Summary, Experience, Education, and Skills.
- Include measurable results only when you can verify the numbers.
Privacy and limitations
- Resume text is sent to Google's Gemini API for analysis. Do not upload a resume unless you are comfortable with that processing and the applicable Google service terms.
- The app does not store uploaded resume files in a database. Streamlit session state keeps the returned analysis for the current session.
- PDF extraction is text-based; scanned PDFs need OCR before upload.
- Tables and unusual layouts can affect extraction quality.
- The app is an educational starter project, not le

AI Resume ATS Analyzer
A Streamlit app that extracts text from PDF, DOCX, and TXT resumes and uses Google Gemini 2.5 Flash to provide an estimated ATS-readiness score, score breakdown, strengths, weaknesses, missing/underused keywords, and actionable improvements.
Important: The score is an AI-generated estimate, not an official score from an employer's ATS and not a prediction of hiring success. Different ATS products and employers use different screening rules.

Features
- Upload PDF, DOCX, or TXT resumes (maximum 10 MB).
- Optional target job title and job description for more relevant feedback.
- Estimated score from 0–100 and five score categories.
- Strengths, weaknesses, keyword gaps, improvement priorities, and ATS formatting tips.
- Suggested professional summary based only on information in the resume.
- Download the analysis as JSON.
- Handles missing keys, empty files, unsupported formats, unreadable/scanned PDFs, and API failures.
1. Requirements
- Python 3.10 or newer (Python 3.11 or 3.12 recommended).
- A Google Gemini API key from Google AI Studio.
- Git and a GitHub account (for deployment).
2. Run locally
Windows PowerShell
# 1. Open this project folder
cd resume-ats-analyzer

# 2. Create and activate a virtual environment
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Set your Gemini API key for this terminal session
$env:GEMINI_API_KEY="YOUR_REAL_GEMINI_API_KEY"

# 5. Start Streamlit
python -m streamlit run app.py
macOS / Linux
cd resume-ats-analyzer
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
export GEMINI_API_KEY="YOUR_REAL_GEMINI_API_KEY"
python -m streamlit run app.py
Open the local URL printed in the terminal (usually http://localhost:8501).
Alternative: local Streamlit secrets
Create .streamlit/secrets.toml:
GEMINI_API_KEY = "YOUR_REAL_GEMINI_API_KEY"
Do not commit this file to GitHub. Add .streamlit/secrets.toml to .gitignore before pushing.
3. Get a Gemini API key
1. Open Google AI Studio.
2. Create or select a project and generate an API key.
3. Keep the key private. Do not paste it into app.py, README.md, screenshots, or a public GitHub repository.
4. Set it as GEMINI_API_KEY using one of the methods above.
The app uses the gemini-2.5-flash model. API availability, quotas, pricing, and model lifecycle are controlled by Google and can change. If Google retires or restricts this model, update MODEL_NAME in app.py to a currently available Flash model in your Google AI Studio project.
4. Push the project to GitHub
Create a new empty repository on GitHub (for example, resume-ats-analyzer). Do not add a README or license there if you already have these files locally.

In the project folder, create a .gitignore file with:
.venv/
__pycache__/
*.py[cod]
.streamlit/secrets.toml
.env
.DS_Store
Then run:
git init
git add app.py README.md requirements.txt .gitignore
git commit -m "Initial resume ATS analyzer app"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/resume-ats-analyzer.git
git push -u origin main
Replace YOUR_GITHUB_USERNAME with your GitHub username. If Git asks you to authenticate, complete the GitHub sign-in flow or use a GitHub Personal Access Token when prompted for HTTPS credentials (never put the token in your source code).

For later updates:
git add .
git commit -m "Describe your changes"
git push
5. Deploy on Streamlit Community Cloud
1. Push the project to GitHub using the steps above.
2. Sign in at Streamlit Community Cloud using the GitHub account that can access your repository.
3. Select Create app.
4. Choose your repository, branch (main), and main file path (app.py).
5. Open Advanced settings before deploying.
6. Choose Python 3.11 or 3.12 if the option is available.
7. In the Secrets field, enter this TOML value:
   GEMINI_API_KEY = "YOUR_REAL_GEMINI_API_KEY"
8. Click Save / Deploy and wait for the build to finish.
9. Open the app URL provided by Streamlit and test with a non-sensitive sample resume.
Streamlit installs packages from requirements.txt. After deployment, pushing code changes to the connected branch normally triggers a redeploy. If the build fails, open the app's Manage app / logs view and read the first dependency or Python error.

Official deployment guide: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy

Official secrets guide: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
6. Common problems
Problem	What to check
GEMINI_API_KEY not found	Check the environment variable locally or the Streamlit Cloud Secrets TOML spelling and quotes. Restart the local app after changing environment variables.
Invalid API key / permission error	Create a valid key in Google AI Studio and confirm the Gemini API is enabled for its project.
Quota / rate-limit error	Check Google AI Studio usage and billing/quota settings; wait or adjust your project limits.
Model not found	Check whether gemini-2.5-flash is available to your project; update MODEL_NAME if Google has changed model availability.
ModuleNotFoundError	Confirm requirements.txt is in the repository root and redeploy after committing it.
PDF has no extracted text	It may be a scanned/image-only PDF. OCR is not included in this version; use a text-based PDF or convert it with OCR first.
DOCX/PDF cannot be read	Try opening and re-saving the file in a trusted document editor, then upload it again.
Deployment fails	Check Streamlit logs, Python version, and dependency installation output.


7. Project structure
resume-ats-analyzer/
├── app.py
├── README.md
├── requirements.txt
└── .gitignore
8. Privacy and responsible use
- Resume contents are sent to Google's Gemini API when the user runs an analysis. Review Google's current API terms and data handling policies before using this app with real candidate data.
- This starter app does not save uploaded resume files to a database or disk intentionally. Streamlit holds the current upload in the running app session while processing.
- Do not upload resumes without the candidate's permission.
- Do not use the AI score as the sole basis for hiring or rejection. Review candidates fairly and manually.
- For a public production app, consider authentication, rate limiting, privacy disclosures, file scanning, monitoring, and explicit retention/deletion policies.
9. Testing checklist
Before publishing, test the app with:
- A text-based PDF, a DOCX, and a TXT resume.
- An empty file and an unsupported file type.
- A scanned PDF (the app should explain that no readable text was found).
- A missing/invalid API key and a valid API key.
- A job description and a run without one.
- A resume with no personally sensitive information.
This project is a starter implementation. No developer can guarantee zero errors across every machine, file, API quota, or cloud deployment. Test with your own API key and sample documents before sharing it publicly.

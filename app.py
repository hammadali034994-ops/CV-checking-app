import json
import os
import re
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
import fitz  # PyMuPDF
from docx import Document

load_dotenv()

def get_secret(name: str, default: str = "") -> str:
    """Read a Streamlit secret when deployed, otherwise use an environment variable."""
    try:
        return str(st.secrets.get(name, os.getenv(name, default)))
    except Exception:
        return os.getenv(name, default)


DEFAULT_MODEL = get_secret("GEMINI_MODEL", "gemini-2.5-flash")
MAX_FILE_MB = 10
ALLOWED_TYPES = ["pdf", "docx", "txt"]

st.set_page_config(
    page_title="Resume ATS Analyzer",
    page_icon="📄",
    layout="wide",
)

SYSTEM_INSTRUCTIONS = """
You are an expert resume reviewer and applicant-tracking-system (ATS) readiness coach.
Analyze only the resume text and the job description provided. Do not invent experience,
skills, qualifications, employers, dates, or achievements. Be constructive and specific.

Return ONLY valid JSON matching this schema:
{
  "ats_score": integer from 0 to 100,
  "score_label": string,
  "summary": string,
  "strengths": [string, ...],
  "issues": [string, ...],
  "missing_keywords": [string, ...],
  "matched_keywords": [string, ...],
  "section_feedback": [{"section": string, "feedback": string}, ...],
  "improvements": [{"priority": "High|Medium|Low", "change": string, "reason": string, "example": string}, ...],
  "formatting_tips": [string, ...],
  "disclaimer": string
}

Scoring guidance:
- If a job description is supplied, assess relevance to that specific role: keyword alignment,
  relevant skills/experience, evidence of impact, and clarity.
- If no job description is supplied, assess general ATS-readiness: standard sections,
  readable structure, relevant skills, measurable accomplishments, and clarity.
- Do not claim to know the score produced by any real ATS. It is an estimate, not a hiring
  prediction. Penalize missing evidence, not a candidate's identity or personal traits.
- Missing keywords must be genuinely relevant to the supplied job description. Never advise
  adding a keyword unless the candidate genuinely has that skill or experience.
- Examples must be truthful templates or rewrites grounded in the supplied resume. Use
  placeholders where a metric or fact is missing; never fabricate metrics.
- Keep the response concise, actionable, and easy to scan.
"""


def extract_resume_text(filename: str, file_bytes: bytes) -> str:
    """Extract text from PDF, DOCX, or TXT uploads."""
    suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix == "pdf":
        with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
            pages = [page.get_text("text") for page in pdf]
        text = "\n".join(pages)
    elif suffix == "docx":
        with tempfile.NamedTemporaryFile(suffix=".docx") as tmp:
            tmp.write(file_bytes)
            tmp.flush()
            document = Document(tmp.name)
        paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
        table_text = [
            " | ".join(cell.text.strip() for cell in row.cells)
            for table in document.tables
            for row in table.rows
        ]
        text = "\n".join(paragraphs + table_text)
    elif suffix == "txt":
        text = file_bytes.decode("utf-8-sig", errors="replace")
    else:
        raise ValueError("Unsupported file type. Upload a PDF, DOCX, or TXT file.")

    # Normalize whitespace while preserving paragraph boundaries.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) < 80:
        raise ValueError(

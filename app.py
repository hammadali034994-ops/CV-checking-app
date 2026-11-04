import json
import os
import re
import tempfile
from typing import Any

import fitz
import streamlit as st
from docx import Document
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

APP_TITLE = "Resume ATS Analyzer"
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_FILE_MB = 10
SUPPORTED_TYPES = ["pdf", "docx", "txt"]


def get_secret(name: str, default: str = "") -> str:
    """Read Streamlit Cloud secrets, falling back to environment variables."""
    try:
        value = st.secrets.get(name, default)
        return str(value) if value else os.getenv(name, default)
    except Exception:
        return os.getenv(name, default)


def extract_resume_text(filename: str, file_bytes: bytes) -> str:
    """Extract text from PDF, DOCX, or TXT resume files."""
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension == "pdf":
        with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
            text = "\n".join(page.get_text("text") for page in pdf.pages)
    elif extension == "docx":
        with tempfile.NamedTemporaryFile(suffix=".docx") as temp_file:
            temp_file.write(file_bytes)
            temp_file.flush()
            document = Document(temp_file.name)
            paragraphs = [
                paragraph.text for paragraph in document.paragraphs
                if paragraph.text.strip()
            ]
            table_rows = []
            for table in document.tables:
                for row in table.rows:
                    table_rows.append(
                        " | ".join(cell.text.strip() for cell in row.cells)
                    )
            text = "\n".join(paragraphs + table_rows)
    elif extension == "txt":
        text = file_bytes.decode("utf-8-sig", errors="replace")
    else:
        raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    if len(text) < 80:
        raise ValueError(
            "Could not extract enough text from this file. If it is a scanned PDF, "
            "please OCR it first or upload a DOCX/TXT copy."
        )
    return text


def parse_model_json(response_text: str) -> dict[str, Any]:
    """Parse and minimally validate the JSON returned by Gemini."""
    cleaned = response_text.strip()
    cleaned = re.sub(r"\A```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```\Z", "", cleaned)

    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace == -1 or last_brace <= first_brace:
        raise ValueError("Gemini returned an invalid response. Please try again.")

    result = json.loads(cleaned[first_brace:last_brace + 1])
    if not isinstance(result, dict):
        raise ValueError("Gemini response must be a JSON object.")

    score = result.get("ats_score")
    if not isinstance(score, (int, float)) or isinstance(score, bool):
        raise ValueError("Gemini response did not include a numeric ATS score.")
    result["ats_score"] = max(0, min(100, int(score)))

    list_fields = [
        "strengths", "issues", "missing_keywords", "matched_keywords",
        "section_feedback", "improvements", "formatting_tips",
    ]
    for field in list_fields:
        if not isinstance(result.get(field), list):
            result[field] = []

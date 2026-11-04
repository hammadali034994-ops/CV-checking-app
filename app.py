"""
AI Resume ATS Analyzer
Run locally with: streamlit run app.py
"""
from __future__ import annotations

import io
import json
import os
import re
from typing import Any

import streamlit as st
from docx import Document
from google import genai
from pypdf import PdfReader

APP_TITLE = "Resume ATS Analyzer"
MODEL_NAME = "gemini-2.5-flash"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_RESUME_CHARS = 30_000

st.set_page_config(page_title=APP_TITLE, page_icon="📄", layout="wide")


def get_api_key() -> str | None:
    """Read the key from Streamlit secrets first, then environment variables."""
    try:
        key = st.secrets.get("GEMINI_API_KEY")
        if key:
            return str(key).strip()
    except Exception:
        # st.secrets raises when no secrets.toml exists; environment fallback is expected.
        pass
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


def extract_resume_text(uploaded_file) -> str:
    """Extract text from PDF, DOCX, or TXT uploaded through Streamlit."""
    if uploaded_file is None:
        raise ValueError("Please upload a resume first.")

    filename = (uploaded_file.name or "").lower()
    file_bytes = uploaded_file.getvalue()

    if not file_bytes:
        raise ValueError("The uploaded file is empty.")
    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError("File is larger than the 10 MB limit.")

    try:
        if filename.endswith(".pdf"):
            reader = PdfReader(io.BytesIO(file_bytes))
            if reader.is_encrypted:
                raise ValueError("This PDF is password-protected. Upload an unlocked PDF.")
            chunks = [(page.extract_text() or "") for page in reader.pages]
            text = "\n".join(chunks)
        elif filename.endswith(".docx"):
            document = Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
            table_text = [
                " | ".join(cell.text.strip() for cell in row.cells)
                for table in document.tables
                for row in table.rows
            ]
            text = "\n".join(paragraphs + table_text)
        elif filename.endswith(".txt"):
            text = file_bytes.decode("utf-8-sig")
        else:
            raise ValueError("Unsupported format. Please upload a PDF, DOCX, or TXT file.")
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(
            "I couldn't read this file. It may be damaged or use an unsupported format."
        ) from exc

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        raise ValueError(
            "No readable text was found. If this is a scanned PDF, convert it using OCR "
            "before uploading."
        )
    return text[:MAX_RESUME_CHARS]


def _clean_list(value: Any, limit: int = 10) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()][:limit]


def normalize_analysis(data: Any) -> dict[str, Any]:
    """Validate and normalize model output before displaying it."""
    if not isinstance(data, dict):

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
        raise ValueError("The AI returned an unexpected response. Please try again.")

    try:
        score = int(float(data.get("ats_score", 0)))
    except (TypeError, ValueError):
        score = 0

    score = max(0, min(100, score))
    breakdown = data.get("score_breakdown", {})
    if not isinstance(breakdown, dict):
        breakdown = {}

    normalized_breakdown = {}
    for key in ("keyword_match", "formatting", "experience", "skills", "education"):
        try:
            value = int(float(breakdown.get(key, 0)))
        except (TypeError, ValueError):
            value = 0
        normalized_breakdown[key] = max(0, min(100, value))

    return {
        "ats_score": score,
        "score_breakdown": normalized_breakdown,
        "summary": str(data.get("summary", "Analysis completed."))[:2000],
        "strengths": _clean_list(data.get("strengths")),
        "weaknesses": _clean_list(data.get("weaknesses")),
        "missing_keywords": _clean_list(data.get("missing_keywords"), 20),
        "improvements": _clean_list(data.get("improvements"), 15),
        "rewritten_summary": str(data.get("rewritten_summary", "")).strip()[:4000],
        "formatting_tips": _clean_list(data.get("formatting_tips"), 10),
        "job_match_notes": str(data.get("job_match_notes", "")).strip()[:2000],
    }


def analyze_resume(resume_text: str, job_description: str, target_role: str, api_key: str):
    """Call Gemini and return structured resume feedback."""
    client = genai.Client(api_key=api_key)
    prompt = f"""
You are an experienced resume reviewer. Evaluate the resume for ATS readability and
relevance. Be specific, constructive, and evidence-based. Do not invent qualifications,
skills, metrics, employers, degrees, or experience that are not present.

Target role: {target_role or "Not specified"}

Job description (optional):
{job_description[:12000] if job_description else "Not provided. Assess general ATS readiness."}

Resume text:
{resume_text}

Return a JSON object with these fields:
- ats_score: integer from 0 to 100, an estimated ATS-readiness score, not a guarantee.
- score_breakdown: object with integer scores 0-100 for keyword_match, formatting,
  experience, skills, education.
- summary: concise overall assessment.
- strengths: array of specific strengths found in the resume.
- weaknesses: array of specific issues or gaps.
- missing_keywords: array of relevant keywords missing or underrepresented. When no job
  description is supplied, provide general role-relevant terms only if a target role exists.
- improvements: prioritized, actionable changes. Do not fabricate facts.
- rewritten_summary: improved professional summary using only information in the resume.
- formatting_tips: ATS-friendly formatting recommendations.
- job_match_notes: explain how the resume aligns with the job description, or state that
  no job description was supplied.

Do not treat the score as a prediction of hiring success. A missing item is not proof the
candidate lacks that qualification; it may simply be absent from the resume.
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "temperature": 0.2,
        },
    )
    response_text = getattr(response, "text", None)
    if not response_text:
        raise ValueError("Gemini returned an empty response. Please try again.")
    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError:
        # Defensive fallback for providers returning a fenced JSON block.
        cleaned = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", response_text, flags=re.I)
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError("Gemini returned unreadable analysis. Please try again.") from exc
    return normalize_analysis(parsed)


def main():
    st.title("📄 AI Resume ATS Analyzer")
    st.caption("Get an estimated ATS-readiness score and practical feedback powered by Gemini.")
    st.info(
        "Your resume is sent to the Gemini API for analysis. Avoid uploading documents "
        "containing information you do not want processed by a third-party AI service."
    )

    with st.sidebar:
        st.header("Analysis settings")
        target_role = st.text_input("Target job title (optional)", placeholder="e.g. Data Analyst")
        st.caption("Add the job description for a more relevant keyword and job-match review.")

    job_description = st.text_area(
        "Paste the job description (optional)",
        height=180,
        placeholder="Paste the job posting here to compare your resume against it...",
    )
    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx", "txt"],
        help="Maximum size: 10 MB. Scanned PDFs without selectable text are not supported.",
    )

    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name} ({len(uploaded_file.getvalue()) / 1024:.1f} KB)")

    analyze_clicked = st.button(
        "Analyze my resume",
        type="primary",
        disabled=uploaded_file is None,
        use_container_width=True,
    )

    if analyze_clicked:
        api_key = get_api_key()
        if not api_key:
            st.error(
                "Gemini API key not found. Set GEMINI_API_KEY in your environment "
                "or Streamlit secrets, then restart the app."
            )
            return

        try:
            resume_text = extract_resume_text(uploaded_file)
            with st.spinner("Gemini is reviewing your resume..."):
                result = analyze_resume(resume_text, job_description, target_role, api_key)
            st.session_state["resume_analysis"] = result
            st.session_state["resume_filename"] = uploaded_file.name
        except ValueError as exc:
            st.error(str(exc))
            return
        except Exception as exc:
            # Keep provider/network details out of the public UI; details remain in server logs.
            st.error(
                "The analysis could not be completed. Check your API key, internet connection, "
                "Gemini API quota, and Streamlit logs, then try again."
            )
            print(f"Gemini analysis error: {type(exc).__name__}: {exc}")
            return

    result = st.session_state.get("resume_analysis")
    if not result:
        st.markdown("---")
        st.markdown("### What you'll receive")
        col1, col2, col3 = st.columns(3)
        col1.metric("ATS score", "0–100", help="Estimated readiness score")
        col2.metric("Keyword review", "Included")
        col3.metric("Action plan", "Included")
        st.caption("Upload a resume and click **Analyze my resume** to begin.")
        return

    st.markdown("---")
    st.subheader(f"Results for {st.session_state.get('resume_filename', 'your resume')}")
    score_col, summary_col = st.columns([1, 2])
    with score_col:
        st.metric("Estimated ATS score", f"{result['ats_score']}/100")
        st.progress(result["ats_score"] / 100)
        if result["ats_score"] >= 80:
            st.success("Strong estimated ATS readiness")
        elif result["ats_score"] >= 60:
            st.warning("Some improvements recommended")
        else:
            st.error("Several improvements recommended")
    with summary_col:
        st.write(result["summary"])
        st.caption("This is an AI-generated estimate, not an official ATS score.")

    st.subheader("Score breakdown")
    labels = {
        "keyword_match": "Keyword match",
        "formatting": "Formatting",
        "experience": "Experience",
        "skills": "Skills",
        "education": "Education",
    }
    cols = st.columns(len(labels))
    for col, (key, label) in zip(cols, labels.items()):
        with col:
            st.metric(label, f"{result['score_breakdown'][key]}/100")

    left, right = st.columns(2)
    with left:
        st.subheader("✅ Strengths")
        if result["strengths"]:
            for item in result["strengths"]:
                st.markdown(f"- {item}")
        else:
            st.write("No specific strengths were returned.")
        st.subheader("⚠️ Weaknesses")
        if result["weaknesses"]:
            for item in result["weaknesses"]:
                st.markdown(f"- {item}")
        else:
            st.write("No specific weaknesses were returned.")
    with right:
        st.subheader("🔎 Missing or underused keywords")
        if result["missing_keywords"]:
            st.write(", ".join(result["missing_keywords"]))
        else:
            st.write("No missing keywords were identified.")
        st.subheader("🛠️ Recommended improvements")
        if result["improvements"]:
            for index, item in enumerate(result["improvements"], start=1):
                st.markdown(f"{index}. {item}")
        else:
            st.write("No improvement suggestions were returned.")

    st.subheader("Professional summary suggestion")
    st.write(result["rewritten_summary"] or "No rewritten summary was returned.")
    st.subheader("ATS-friendly formatting tips")
    if result["formatting_tips"]:
        for item in result["formatting_tips"]:
            st.markdown(f"- {item}")
    else:
        st.write("No formatting tips were returned.")
    st.subheader("Job match notes")
    st.write(result["job_match_notes"] or "No additional job-match notes.")

    download_data = json.dumps(result, indent=2, ensure_ascii=False)
    st.download_button(
        "Download analysis (JSON)",
        data=download_data,
        file_name="resume_ats_analysis.json",
        mime="application/json",
    )
    if st.button("Clear results"):
        st.session_state.pop("resume_analysis", None)
        st.session_state.pop("resume_filename", None)
        st.rerun()


if __name__ == "__main__":
    main()

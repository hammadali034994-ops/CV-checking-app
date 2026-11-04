        "Upload your resume",
        type=ALLOWED_TYPES,
        help="Supported formats: PDF, DOCX, TXT. Scanned PDFs may need OCR first.",
    )
    job_description = st.text_area(
        "Paste the job description (recommended)",
        height=190,
        placeholder="Paste the target job description here. Leave blank for a general ATS-readiness review.",
    )

    if uploaded_file is not None:
        if uploaded_file.size > MAX_FILE_MB * 1024 * 1024:
            st.error(f"File is too large. Please upload a file under {MAX_FILE_MB} MB.")
            st.stop()
        st.success(f"Uploaded: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

    analyze_clicked = st.button(
        "Analyze resume",
        type="primary",
        disabled=uploaded_file is None,
        use_container_width=True,
    )

    if analyze_clicked and uploaded_file is not None:
        try:
            with st.spinner("Reading your resume and analyzing it with Gemini..."):
                resume_text = extract_resume_text(
                    uploaded_file.name, uploaded_file.getvalue()
                )
                result = analyze_resume(
                    resume_text, job_description, api_key, model_name.strip() or DEFAULT_MODEL
                )
            st.session_state["analysis_result"] = result
            st.session_state["analysis_filename"] = uploaded_file.name
        except (ValueError, json.JSONDecodeError) as exc:
            st.error(str(exc))
        except Exception as exc:
            # Avoid exposing request details or secrets in the UI.
            st.error(
                "Analysis failed. Check your API key, model name, internet connection, "
                "and Gemini API quota, then try again."
            )
            st.caption(f"Technical detail: {type(exc).__name__}")

    result = st.session_state.get("analysis_result")
    if result:
        st.divider()
        st.header(f"Analysis: {st.session_state.get('analysis_filename', 'Resume')}")
        score_col, label_col = st.columns([1, 3])
        with score_col:
            st.metric("Estimated ATS score", f"{result['ats_score']}/100")
        with label_col:
            st.subheader(result.get("score_label", "ATS readiness"))
            st.write(result.get("summary", ""))

        st.progress(result["ats_score"] / 100)
        left, right = st.columns(2)
        with left:
            render_list("Strengths", result.get("strengths", []))
            render_list("Matched keywords", result.get("matched_keywords", []))
            render_list("Formatting tips", result.get("formatting_tips", []))
        with right:
            render_list("Issues to address", result.get("issues", []))
            render_list("Potential missing keywords", result.get("missing_keywords", []))
        st.subheader("Section-by-section feedback")
        for item in result.get("section_feedback", []):
            with st.expander(item.get("section", "Section")):
                st.write(item.get("feedback", ""))
        st.subheader("Recommended improvements")
        improvements = result.get("improvements", [])
        if improvements:
            for i, item in enumerate(improvements, start=1):
                with st.expander(
                    f"{i}. [{item.get('priority', 'Medium')}] {item.get('change', 'Suggested change')}",
                    expanded=(i == 1),
                ):
                    st.write(item.get("reason", ""))
                    if item.get("example"):
                        st.markdown("**Example**")
                        st.write(item["example"])
        else:
            st.caption("No specific improvements were returned.")
        st.caption(
            result.get(
                "disclaimer",
                "This is an AI-generated estimate. Verify all recommendations and keep your resume truthful.",
            )
        )

        report = json.dumps(result, indent=2, ensure_ascii=False)
        st.download_button(
            "Download analysis (JSON)",
            data=report,
            file_name="resume_analysis.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()

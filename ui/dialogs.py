import io
import pandas as pd
import streamlit as st
from services.data_service import clean_dataframe_for_corruption, parse_csv_with_recovery

MAX_UPLOAD_MB = 250
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024


@st.dialog("Upload Your Data")
def upload_data_dialog():
    st.write("Upload a CSV file to begin your analysis.")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        if len(file_bytes) > MAX_UPLOAD_BYTES:
            st.error("File is too large. Max upload size is 250 MB.")
            return

        cache_key = f"{uploaded_file.name}:{len(file_bytes)}"
        if st.session_state.get("upload_cache_key") != cache_key:
            with st.spinner("Checking and cleaning CSV..."):
                try:
                    raw_df, parse_report = parse_csv_with_recovery(file_bytes)
                    clean_df, report = clean_dataframe_for_corruption(
                        raw_df,
                        parse_report.get("source_rows", len(raw_df)),
                        parse_report=parse_report,
                    )

                    st.session_state.dataset = clean_df
                    st.session_state.clean_report = report
                    st.session_state.uploaded_file_name = uploaded_file.name
                    st.session_state.data_ready = True
                    st.session_state.last_result = None
                    st.session_state.last_plan = None
                    st.session_state.chat_history = []
                    st.session_state.upload_cache_key = cache_key
                except Exception as ex:
                    st.session_state.data_ready = False
                    st.error(f"Could not process this file: {ex}")
                    return

        report = st.session_state.get("clean_report", {})
        st.success("CSV accepted and cleaned successfully.")
        st.caption("We detected and removed malformed/noisy rows before using the dataset.")

        c1, c2, c3 = st.columns(3)
        c1.metric("Rows kept", report.get("row_count", 0))
        c2.metric("Rows auto-repaired", report.get("malformed_fixed", 0))
        c3.metric("Sparse rows removed", report.get("removed_sparse_rows", 0))

        with st.expander("Cleaning steps", expanded=True):
            st.markdown(
                f"""
1. Loaded file using robust AI-simulated parser (`{report.get('parser', 'unknown')}`) with delimiter `{report.get('delimiter', ',')}`.
2. Auto-repaired (padded/truncated) malformed rows: `{report.get('malformed_fixed', 0)}`.
3. Dropped empty rows: `{report.get('empty_rows', 0)}`.
4. Removed sparse/noisy rows: `{report.get('removed_sparse_rows', 0)}`.
5. Final usable dataset: `{report.get('row_count', 0)}` rows and `{report.get('column_count', 0)}` columns.
                """
            )

        if st.button("Open Chat Workspace", type="primary", width="stretch"):
            st.session_state.page = "workspace"
            st.rerun()

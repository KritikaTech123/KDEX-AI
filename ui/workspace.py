import streamlit as st
from services.data_service import run_sql_query
from services.llm_service import ask_llm_for_plan, compose_answer_from_results, fallback_plan
from ui.dialogs import upload_data_dialog
from utils.charting import infer_chart_type, render_chart


def run_assistant_turn(user_prompt: str) -> str:
    dataset = st.session_state.dataset
    columns = list(dataset.columns)
    
    # Grab the first 5 rows to provide the AI with data context so it knows exactly what the values look like.
    try:
        sample_data = dataset.head(5).to_dict(orient="records")
    except Exception:
        sample_data = []

    try:
        plan = ask_llm_for_plan(user_prompt, columns, st.session_state.chat_history, sample_data)
    except Exception:
        plan = fallback_plan(user_prompt, columns)

    queries = plan.get("analysis_queries", [])
    execution_log = []
    final_result_df = None

    for idx, query_item in enumerate(queries[:3]):
        sql = str(query_item.get("sql", "")).strip()
        if not sql:
            continue
        try:
            result_df = run_sql_query(dataset, sql)
            sample_rows = result_df.head(12).to_dict(orient="records")
            execution_log.append(
                {
                    "name": query_item.get("name", f"q{idx + 1}"),
                    "purpose": query_item.get("purpose", ""),
                    "sql": sql,
                    "row_count": int(len(result_df)),
                    "columns": list(result_df.columns),
                    "sample_rows": sample_rows,
                }
            )
        except Exception as ex:
            execution_log.append(
                {
                    "name": query_item.get("name", f"q{idx + 1}"),
                    "purpose": query_item.get("purpose", ""),
                    "sql": sql,
                    "error": str(ex),
                }
            )

    final_sql = str(plan.get("final_query", "")).strip()
    if final_sql:
        try:
            final_result_df = run_sql_query(dataset, final_sql)
        except Exception:
            final_result_df = None

    if final_result_df is None:
        for item in execution_log:
            if "sample_rows" in item and item["sample_rows"]:
                final_sql = item["sql"]
                final_result_df = run_sql_query(dataset, final_sql)
                break

    if final_result_df is None:
        final_sql = "SELECT * FROM dataset LIMIT 10"
        final_result_df = run_sql_query(dataset, final_sql)

    try:
        assistant_answer = compose_answer_from_results(user_prompt, st.session_state.chat_history, execution_log)
    except Exception:
        if len(final_result_df) == 1 and len(final_result_df.columns) >= 1:
            first_col = final_result_df.columns[0]
            assistant_answer = f"Based on your data, the result is {final_result_df.iloc[0][first_col]}."
        else:
            assistant_answer = "I analyzed your data and prepared the result with chart insights."

    plan["final_query"] = final_sql
    plan["chart_type"] = infer_chart_type(final_result_df, plan.get("chart_type"))
    plan["executed_queries"] = execution_log

    st.session_state.last_result = final_result_df
    st.session_state.last_plan = plan

    return assistant_answer


def render_right_panel() -> None:
    st.markdown("### Insights")
    st.caption("Auto-generated charts based on your questions.")

    if st.session_state.last_result is None or st.session_state.last_plan is None:
        st.info("Charts and data will appear here after you chat with KDEX.")
        return

    result_df = st.session_state.last_result
    plan = st.session_state.last_plan

    render_chart(result_df, plan.get("chart_type", "table"), plan.get("x_axis"), plan.get("y_axis"))

    show_details = st.toggle("Show table and SQL details", value=False)
    if show_details:
        st.dataframe(result_df, width="stretch")
        st.code(plan.get("final_query", ""), language="sql")
        executed = plan.get("executed_queries", [])
        if executed:
            st.markdown("**Executed analysis queries**")
            for item in executed:
                st.caption(f"{item.get('name', 'query')} - {item.get('purpose', '')}")
                st.code(item.get("sql", ""), language="sql")


def render_workspace() -> None:
    if not st.session_state.data_ready:
        st.session_state.page = "landing"
        st.rerun()

    # Top Bar Header
    head_left, head_right = st.columns([10, 2], vertical_alignment="center")
    with head_left:
        st.markdown(
            f"### 🌊 KDEX - Your AI Data Analyst "
            f"<span style='font-size: 14px; font-weight: normal; color: #64748b; margin-left: 12px;'>"
            f"Analyzing: {st.session_state.uploaded_file_name}</span>", 
            unsafe_allow_html=True
        )
    with head_right:
        if st.button("Upload New", use_container_width=True):
            upload_data_dialog()

    st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 1rem;'/>", unsafe_allow_html=True)

    # Wider chat panel for better readability while keeping a larger chart side.
    chat_col, chart_col = st.columns([6, 6], gap="large")

    with chat_col:
        st.markdown("### Chat")
        
        chat_box = st.container(height=650)
        with chat_box:
            # Fixed greeting
            with st.chat_message("assistant"):
                st.markdown("Hi! I am **KDEX**, your AI data analyst. Ask me any question regarding your data and I'll generate insights and charts for you.")
                
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        user_prompt = st.chat_input("Ask KDEX about your data...")
        active_prompt = user_prompt or st.session_state.get("queued_prompt", "")
        if active_prompt:
            st.session_state.queued_prompt = ""
            st.session_state.chat_history.append({"role": "user", "content": active_prompt})
            
            with chat_box:
                with st.chat_message("user"):
                    st.write(active_prompt)
                
                with st.spinner("Analyzing..."):
                    assistant_text = run_assistant_turn(active_prompt)
                
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_text})
            st.rerun()

    with chart_col:
        with st.container(height=800, border=False):
            render_right_panel()

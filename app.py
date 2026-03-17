import streamlit as st

from ui.landing import render_landing_page
from ui.workspace import render_workspace


def init_state() -> None:
    if "page" not in st.session_state:
        st.session_state.page = "landing"
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "last_plan" not in st.session_state:
        st.session_state.last_plan = None
    if "data_ready" not in st.session_state:
        st.session_state.data_ready = False
    if "dataset" not in st.session_state:
        st.session_state.dataset = None
    if "clean_report" not in st.session_state:
        st.session_state.clean_report = None
    if "uploaded_file_name" not in st.session_state:
        st.session_state.uploaded_file_name = ""
    if "queued_prompt" not in st.session_state:
        st.session_state.queued_prompt = ""


def apply_global_styles() -> None:
    # Conditional max-width: keep landing page centered, but let workspace expand.
    max_width_css = "1220px" if st.session_state.get("page") == "landing" else "98%"
    
    st.markdown(
        f"""
        <style>
            .stApp {{
                background:
                    radial-gradient(1200px 500px at 85% -5%, #d6f0ff 0%, rgba(214, 240, 255, 0) 70%),
                    radial-gradient(1000px 420px at -5% 10%, #fdecc8 0%, rgba(253, 236, 200, 0) 65%),
                    #f7fafc;
                color: #0f172a;
            }}
            [data-testid="stSidebar"] {{
                display: none;
            }}
            .block-container {{
                max-width: {max_width_css};
                padding-top: 1rem;
                padding-bottom: 1rem;
            }}
            div[data-testid="stChatMessage"] {{
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                padding: 0.65rem 0.85rem;
                box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
                margin-bottom: 0.65rem;
            }}
            div[data-testid="stChatMessage"][data-testid*="assistant"] {{
                background: #ffffff;
            }}
            div[data-testid="stChatMessage"][data-testid*="user"] {{
                background: #f0f9ff;
            }}
            div[data-testid="stDialog"] h2 {{
                letter-spacing: 0.2px;
            }}
            /* Slightly darker Chat Input container background without making the input text dark */
            div[data-testid="stChatInput"] {{
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-radius: 12px;
            }}
            
            /* Tiny inline follow-up pills */
            .small-font-button {{
                display: flex;
                flex-direction: row;
                flex-wrap: wrap;
                gap: 4px;
                margin-top: 2px;
                margin-bottom: 2px;
            }}
            .small-font-button div[data-testid="stButton"] {{
                padding: 0 !important;
                margin: 0 !important;
                width: auto !important;
            }}
            .small-font-button button {{
                font-size: 0.75rem !important;
                padding: 0.1rem 0.5rem !important;
                min-height: 20px !important;
                line-height: 1.2 !important;
                border: 1px solid #94a3b8 !important;
                background-color: #ffffff !important;
                box-shadow: none !important;
                border-radius: 12px !important;
                width: auto !important;
            }}
            
            /* Make chart side height-dynamic but chat scrollable inside container */
            .chat-scroll-area {{
                height: 70vh !important;
                overflow-y: auto !important;
                overflow-x: hidden !important;
                padding-right: 8px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="KDEX", page_icon="K", layout="wide")
    init_state()
    apply_global_styles()

    if st.session_state.page == "landing":
        render_landing_page()
        return

    render_workspace()


if __name__ == "__main__":
    main()

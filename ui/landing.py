import streamlit as st

from ui.dialogs import upload_data_dialog


def _open_upload_dialog() -> None:
    upload_data_dialog()


def render_landing_page() -> None:
    st.markdown(
        """
        <style>
            .kdex-nav {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.25rem 0.1rem 1.25rem 0.1rem;
            }
            .kdex-logo {
                font-size: 1.1rem;
                font-weight: 800;
                letter-spacing: 0.2px;
                color: #0f172a;
            }
            .kdex-chip {
                display: inline-block;
                background: #e0f2fe;
                color: #0c4a6e;
                border: 1px solid #bae6fd;
                border-radius: 999px;
                padding: 0.22rem 0.7rem;
                font-size: 0.8rem;
                font-weight: 700;
            }
            .kdex-hero {
                border: 1px solid #dbeafe;
                border-radius: 24px;
                background:
                    radial-gradient(700px 250px at 80% 0%, #dbeafe 0%, rgba(219, 234, 254, 0) 70%),
                    linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
                padding: 2.6rem 2.4rem;
                box-shadow: 0 14px 35px rgba(15, 23, 42, 0.08);
                margin-bottom: 1.2rem;
            }
            .kdex-title {
                font-size: 3rem;
                line-height: 1.1;
                font-weight: 800;
                color: #0b1220;
                margin-bottom: 0.8rem;
                max-width: 860px;
            }
            .kdex-sub {
                font-size: 1.06rem;
                line-height: 1.7;
                color: #334155;
                max-width: 760px;
            }
            .kdex-section {
                margin-top: 1.2rem;
                border: 1px solid #e2e8f0;
                border-radius: 20px;
                background: #ffffff;
                padding: 1.2rem 1.2rem;
                box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
            }
            .kdex-card {
                border: 1px solid #e5e7eb;
                border-radius: 16px;
                background: #ffffff;
                padding: 1rem 1rem;
                min-height: 190px;
            }
            .kdex-card h4 {
                margin: 0 0 0.45rem 0;
                color: #0f172a;
                font-size: 1rem;
            }
            .kdex-card p {
                margin: 0;
                color: #475569;
                line-height: 1.55;
                font-size: 0.94rem;
            }
            .kdex-muted {
                color: #475569;
                line-height: 1.68;
                font-size: 0.97rem;
            }
            .kdex-footer-cta {
                text-align: center;
                padding: 1.3rem 1rem 0.1rem 1rem;
            }
            .kdex-foot {
                text-align: center;
                color: #64748b;
                font-size: 0.88rem;
                margin-top: 0.6rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="kdex-nav">
          <div class="kdex-logo">KDEX</div>
          <div class="kdex-chip">Built for non-technical teams</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="kdex-hero">
          <div class="kdex-title">Ask questions. Get insights. Make decisions faster.</div>
          <div class="kdex-sub">
            KDEX turns your CSV into a conversational analytics workspace. Instead of learning SQL,
            dashboards, or pivot tables, you can simply ask: <b>"Why did revenue drop in February?"</b>
            or <b>"Show top 10 customers by growth"</b>. KDEX interprets intent, runs safe queries,
            and produces charts your team can understand in seconds.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    top_a, top_b, top_c = st.columns(3)
    top_a.metric("Time To First Insight", " Around 60 sec")
    top_b.metric("Maximum CSV Size", "250 MB")
    top_c.metric("Interaction Style", "Natural Language")

    st.markdown('<div class="kdex-section">', unsafe_allow_html=True)
    st.subheader("Why Teams Use KDEX")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="kdex-card">
              <h4>Conversation-first analysis</h4>
              <p>
                Anyone can ask follow-up questions naturally. KDEX keeps recent chat context,
                so you can continue from earlier answers without repeating full instructions.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="kdex-card">
              <h4>Chart-focused output</h4>
              <p>
                Results prioritize visuals for non-technical users. Tables and SQL stay hidden
                by default and are available only when you explicitly choose to inspect details.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            <div class="kdex-card">
              <h4>Safe and practical</h4>
              <p>
                Queries are restricted to SELECT-only operations on an in-memory dataset.
                This keeps the workflow simple, safe, and consistent for rapid exploration.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    about_col, how_col = st.columns(2, gap="large")

    with about_col:
        st.markdown('<div class="kdex-section">', unsafe_allow_html=True)
        st.subheader("About KDEX")
        st.markdown(
            """
            <div class="kdex-muted">
              KDEX was designed for founders, operations teams, sales managers, and analysts who
              need answers quickly but do not want to maintain a heavy BI stack. It combines an
              intuitive chat interface with robust data processing so your team can move from raw
              spreadsheet data to clear decisions in one place.<br><br>
              The experience is intentionally simple: upload, ask, inspect chart, follow up.
              No schema setup wizard, no SQL editor pressure, and no dashboard building overhead.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with how_col:
        st.markdown('<div class="kdex-section">', unsafe_allow_html=True)
        st.subheader("How It Works")
        st.markdown(
            """
            <div class="kdex-muted">
              1. Click <b>Try Now</b> and upload a CSV file.<br>
              2. Ask questions in plain language, like <b>"Show monthly trend"</b>.<br>
              3. KDEX generates a safe query and returns a readable answer.<br>
              4. The right panel highlights charts for quick understanding.<br>
              5. Ask follow-up questions and KDEX uses recent conversation context.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    faq = st.expander("Common Questions", expanded=False)
    with faq:
        st.markdown(
            """
- **Do I need SQL knowledge?** No. KDEX is chat-first and non-technical by design.
- **Can I upload another file later?** Yes. The workspace includes a compact `Upload New` action.
- **Where is the API key configured?** In `.streamlit/secrets.toml` under `[api]` using `groq_key`.
- **Does KDEX remember context?** Yes, recent chat turns are included for better follow-up responses.
            """
        )

    st.markdown('<div class="kdex-footer-cta">', unsafe_allow_html=True)
    _, center_cta, _ = st.columns([1, 1.3, 1])
    with center_cta:
        if st.button("Try Now", type="primary", width="stretch"):
            _open_upload_dialog()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="kdex-foot">KDEX • Conversational analytics for everyday business data</div>', unsafe_allow_html=True)

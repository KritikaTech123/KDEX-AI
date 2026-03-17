# KDEX - AI Data Analyst

**Try it Live**: [https://kdex-ai.streamlit.app](https://kdex-ai.streamlit.app)

*Developer: Kritika*

**KDEX** is an intelligent, natural-language data analysis workspace. Upload any CSV dataset, and KDEX leverages a powerful local DuckDB execution engine paired with a sophisticated Groq LLM reasoning pipeline to let you intuitively ask questions about your data.

## Features
- 📊 **Smart Statistical CSV Recovery**: Automatically fixes malformed rows, pads missing headers, and rescues corrupt data without failing.
- 🧠 **Dual-Pipeline AI Logic**: Splits query generation (strict JSON planner) from conversational analysis (Markdown generation) for perfect reliability.
- ⚡ **DuckDB Powered**: In-memory SQL execution means lightning-fast chart rendering.
- 🎨 **Responsive UI**: Expanded workspace logic, clean visual components, zero chat-clutter, and dynamic multi-column layouts.

## Run on Local Server

**Step-by-step Quickstart:**

1. **Clone the repository & enter the folder:**
   ```bash
   git clone <repo_url>
   cd kdex/KDEX
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment:**
   * On Linux/Mac:
     ```bash
     source .venv/bin/activate
     ```
   * On Windows:
     ```cmd
     .venv\Scripts\activate
     ```

4. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Secrets:**
   Create a folder named `.streamlit` at the root of your `KDEX` directory and inside it, create a `secrets.toml` file:
   ```bash
   mkdir .streamlit
   touch .streamlit/secrets.toml
   ```
   Add your Groq API key to the `secrets.toml` file exactly like this:
   ```toml
   groq_key = "gsk_xxxx..."
   ```

6. **Start the Streamlit Server:**
   ```bash
   streamlit run app.py
   ```

Enjoy talking to your data!

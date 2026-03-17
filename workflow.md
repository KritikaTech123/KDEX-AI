# KDEX - Workflow & Technical Architecture

Welcome to the KDEX workflow overview! This document is designed for hackathon participants to understand the engine, technology choices, and operational logic that powers KDEX.

## Tech Stack Overview
- **UI Framework:** Streamlit (chosen for rapid Python UI component wiring, specifically native markdown support & data grids)
- **Data Engine:** DuckDB (chosen for robust, in-memory SQL execution directly against Python structures/DataFrames without database networking overhead)
- **AI/LLM Provider:** Groq executing `llama-3.3-70b-versatile` (chosen for ultra-fast token streaming and excellent mathematical/code reasoning capabilities)
- **Primary Languages:** Python 3.9+
- **Data Handling:** Pandas & native Python `csv` (Sniffer + Statistical fault recovery)

## Core Architectural Philosophies
We recognized that asking AI to generate *and* execute SQL, then format the response all in a single query often leads to hallucinations or logic collapses. To combat this, KDEX uses a decoupled, fault-tolerant **Two-Stage Pipeline**.

### 1. Robust Data Ingestion
Real-world CSVs used in hackathons are historically messy. `pd.read_csv` frequently crashes.
- Our data processor uses Python's native `csv.Sniffer` to detect dialects.
- We utilize **Statistical Mode Row Interpolation** to determine the most common row length in a file.
- If a row is shorter than the median, we automatically pad it with `None` limits.
- If a row is longer, we truncate safely.
- *Result:* 100% resilient ingestion of dirty datasets.

### 2. The AI JSON Planner (Stage 1)
User types: "Show me a pie chart of sales by region."
- We provide the LLM with the schema definitions mapped from DuckDB.
- The LLM constructs a strict **JSON Planner Object** under a Temperature of `0.0` (eliminating hallucination variability).
- The JSON object defines the SQL statement needed and whether a chart component should be generated:
  ```json
  {
      "sql_query": "SELECT Region, SUM(Sales) as Total FROM dataset GROUP BY Region",
      "chart_type": "pie",
      "insights_needed": true
  }
  ```

### 3. Execution (DuckDB Bridge)
- DuckDB executes the raw SQL mapped out by the JSON Planner strictly against the in-memory pandas dataframe alias.
- A subset of that result is captured securely.

### 4. Natural Language Synthesis (Stage 2)
- The numerical matrix and query details from Stage 1 are passed into a second LLM request.
- Temperature is increased to `0.2` to allow for conversational phrasing.
- The AI responds with a cleanly formatted Markdown response summarizing the SQL execution accurately, and appends a **Suggested Follow-ups** section dynamically at the bottom.

## Hackathon Impact Components
* High fault tolerance means judging demos won't crash when testing edge-case files.
* Sub-second insights driven by locally executed DuckDB queries combined with fast Groq token rates.

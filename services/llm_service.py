import json
import os
import re
from typing import Any, Dict, List

import requests
import streamlit as st

DEFAULT_MODEL = "llama-3.3-70b-versatile"


def extract_json_object(raw_text: str) -> Dict[str, Any]:
    stripped = raw_text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\n?", "", stripped).strip()
        stripped = re.sub(r"\n?```$", "", stripped).strip()

    try:
        data = json.loads(stripped, strict=False)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", raw_text)
    if match:
        try:
            return json.loads(match.group(0), strict=False)
        except json.JSONDecodeError:
            pass
            
    # As a secondary fallback for really broken LLM json string answers
    try:
        escaped = raw_text.replace("\n", "\\n")
        match = re.search(r"\{[\s\S]*\}", escaped)
        if match:
            return json.loads(match.group(0), strict=False)
    except json.JSONDecodeError:
        pass

    raise ValueError("AI response was not valid JSON.")


def _extract_json_array(raw_text: str) -> List[Dict[str, Any]]:
    stripped = raw_text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?", "", stripped).strip()
        stripped = re.sub(r"```$", "", stripped).strip()

    try:
        data = json.loads(stripped)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    match = re.search(r"\[[\s\S]*\]", raw_text)
    if not match:
        raise ValueError("AI response was not valid JSON array.")
    data = json.loads(match.group(0))
    if not isinstance(data, list):
        raise ValueError("AI response array parse failed.")
    return data


def get_api_key() -> str | None:
    if "api" in st.secrets and "groq_key" in st.secrets["api"]:
        return st.secrets["api"]["groq_key"]
    if "GROQ_API_KEY" in st.secrets:
        return st.secrets["GROQ_API_KEY"]
    return os.getenv("GROQ_API_KEY")


def _call_groq(messages: List[Dict[str, str]], temperature: float = 0.1, timeout: int = 45) -> str:
    api_key = get_api_key()
    if not api_key:
        raise ValueError("Groq API key is not configured.")

    payload = {
        "model": DEFAULT_MODEL,
        "temperature": temperature,
        "messages": messages,
    }

    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=timeout,
    )
    if not resp.ok:
        raise ValueError(f"LLM API Error: {resp.text}")
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def build_system_prompt(columns: List[str], chat_history: List[Dict[str, str]]) -> str:
    history_lines = []
    for msg in chat_history[-8:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        history_lines.append(f"{role.upper()}: {content}")

    history_block = "\n".join(history_lines) if history_lines else "(no previous messages yet)"
    column_block = ", ".join([f'"{col}"' for col in columns])

    return f"""
You are KDEX AI, a data assistant for non-technical users.
Use only DuckDB SQL over a single table named dataset.
Rules:
1) Always return strict JSON only. No markdown formatting outside of JSON.
2) JSON shape: {{"answer": "short friendly plain-language answer", "sql": "a single SELECT query", "chart_type": "bar|line|area|pie|scatter|table", "x_axis": "column name for x", "y_axis": "column name for y"}}
3) Keep wording non-technical.
4) Use prior conversation for context.
5) Quote column names using double quotes whenever needed.
6) Never produce non-SELECT SQL.
Available columns in dataset: {column_block}
Recent chat context: {history_block}
""".strip()


def build_planner_prompt(columns: List[str], chat_history: List[Dict[str, str]], user_prompt: str, sample_data: List[Dict[str, Any]] = None) -> str:
        history_lines = []
        for msg in chat_history[-8:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_lines.append(f"{role.upper()}: {content}")

        history_block = "\n".join(history_lines) if history_lines else "(no previous messages yet)"
        column_block = ", ".join([f'"{col}"' for col in columns])
        
        sample_block = ""
        if sample_data:
            sample_json = json.dumps(sample_data, ensure_ascii=False, indent=2)
            sample_block = f"Sample rows from dataset (first 5 rows):\n{sample_json}\n"

        return f"""
You are KDEX SQL planner.
Dataset table name: dataset.
Allowed SQL: SELECT only.

{sample_block}

Goal:
Plan 1-3 SQL queries to answer the user accurately, then pick one final query for visualization.

Rules:
1) Return STRICT JSON only with this shape:
{{
    "analysis_queries": [
        {{"name": "short_name", "purpose": "why this query", "sql": "SELECT ..."}}
    ],
    "final_query": "SELECT ...",
    "chart_type": "bar|line|area|pie|scatter|table",
    "x_axis": "column_for_x_or_empty",
    "y_axis": "column_for_y_or_empty"
}}
2) Use 1 query for simple asks, up to 3 for complex asks.
3) If the user asks for comparison/ranking/trend, final_query should be compact (not huge raw table), usually aggregated and <= 15 rows.
4) Never return non-SELECT SQL.
5) Quote column names using double quotes when needed.
6) Avoid `SELECT *` unless user explicitly requests full raw data.
7) Prefer GROUP BY, ORDER BY, and LIMIT for insight-style questions.

Available columns in dataset:
{column_block}

Recent chat context:
{history_block}

Current user request:
{user_prompt}
""".strip()


def build_answer_prompt(user_prompt: str, chat_history: List[Dict[str, str]], results_payload: List[Dict[str, Any]]) -> str:
        history_lines = []
        for msg in chat_history[-8:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_lines.append(f"{role.upper()}: {content}")
        history_block = "\n".join(history_lines) if history_lines else "(no previous messages yet)"

        compact_results = json.dumps(results_payload, ensure_ascii=True)

        return f"""
You are KDEX AI, a user-friendly data analyst.

Write a beautifully structured Markdown answer based ONLY on the SQL results provided.

Rules:
1) Use rich Markdown! Bold key numbers, use bullet points, and use newlines/short paragraphs for readability.
2) Mention key numbers and comparisons. Do not write a massive unreadable chunk of text.
3) If a direct question is asked (e.g., "highest revenue region"), answer directly in the first sentence.
4) If confidence is low due to empty data, say so clearly.
5) Do not mention SQL, JSON, or internal planning.
6) ALWAYS append a final section at the very end titled "**Suggested Follow-ups**" with 2-3 bullet point ideas of what the user should ask next.
7) Return strict JSON only: {{"answer": "Your markdown formatted string"}}

Recent conversation:
{history_block}

Current user question:
{user_prompt}

SQL result snapshots:
{compact_results}
""".strip()


def ask_llm_for_plan(prompt: str, columns: List[str], chat_history: List[Dict[str, str]], sample_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    planner_prompt = build_planner_prompt(columns, chat_history, prompt, sample_data)
    content = _call_groq(
        [
            {"role": "system", "content": "You are a strict JSON SQL planner."},
            {"role": "user", "content": planner_prompt},
        ],
        temperature=0.0,
    )
    plan = extract_json_object(content)

    queries = plan.get("analysis_queries")
    if not isinstance(queries, list) or not queries:
        raise ValueError("Planner returned no analysis queries.")

    for q in queries:
        if not isinstance(q, dict) or not q.get("sql"):
            raise ValueError("Planner query format invalid.")

    if not plan.get("final_query"):
        plan["final_query"] = queries[-1]["sql"]

    return plan


def compose_answer_from_results(user_prompt: str, chat_history: List[Dict[str, str]], results_payload: List[Dict[str, Any]]) -> str:
    content = _call_groq(
        [
            {"role": "system", "content": "You are a strict JSON answer writer."},
            {"role": "user", "content": build_answer_prompt(user_prompt, chat_history, results_payload)},
        ],
        temperature=0.2,
    )
    answer_obj = extract_json_object(content)
    answer = str(answer_obj.get("answer", "")).strip()
    if not answer:
        return "I analyzed your data and prepared the result."
    return answer


def generate_followup_questions(
    user_prompt: str,
    chat_history: List[Dict[str, str]],
    results_payload: List[Dict[str, Any]],
) -> List[str]:
    history_lines = []
    for msg in chat_history[-8:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        history_lines.append(f"{role.upper()}: {content}")
    history_block = "\n".join(history_lines) if history_lines else "(no previous messages yet)"

    compact_results = json.dumps(results_payload, ensure_ascii=True)
    prompt = f"""
You generate next best follow-up analytics questions for non-technical users.

Return strict JSON only with this shape:
{{"follow_up_questions": ["question 1", "question 2", "question 3"]}}

Rules:
1) Provide 2-3 concise, natural follow-up questions.
2) Questions should build on previous result context.
3) Keep each question under 100 characters.
4) No SQL in questions.

Recent conversation:
{history_block}

Current user message:
{user_prompt}

Result snapshots:
{compact_results}
""".strip()

    content = _call_groq(
        [
            {"role": "system", "content": "You are a strict JSON follow-up generator."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )
    data = extract_json_object(content)
    raw_questions = data.get("follow_up_questions", [])
    if not isinstance(raw_questions, list):
        return []

    normalized: List[str] = []
    for item in raw_questions:
        text = str(item).strip()
        if not text:
            continue
        if len(text) > 140:
            text = text[:140].rstrip()
        normalized.append(text)

    return normalized[:3]


def fallback_plan(prompt: str, columns: List[str]) -> Dict[str, Any]:
    if prompt.strip().lower().startswith("select"):
        return {
            "analysis_queries": [
                {"name": "direct_sql", "purpose": "User provided SQL", "sql": prompt.strip()},
            ],
            "final_query": prompt.strip(),
            "chart_type": "table",
            "x_axis": columns[0] if columns else "",
            "y_axis": columns[1] if len(columns) > 1 else (columns[0] if columns else ""),
        }

    safe_cols = ", ".join([f'"{c}"' for c in columns[:8]])
    return {
        "analysis_queries": [
            {
                "name": "preview",
                "purpose": "Fallback preview when planner fails",
                "sql": f"SELECT {safe_cols} FROM dataset LIMIT 12",
            }
        ],
        "final_query": f"SELECT {safe_cols} FROM dataset LIMIT 12",
        "chart_type": "table",
        "x_axis": columns[0] if columns else "",
        "y_axis": columns[1] if len(columns) > 1 else (columns[0] if columns else ""),
    }

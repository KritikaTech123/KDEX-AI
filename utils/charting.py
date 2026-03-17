from typing import Tuple

import altair as alt
import pandas as pd
import streamlit as st


def infer_chart_type(result_df: pd.DataFrame, requested: str | None = None) -> str:
    if result_df.empty or len(result_df.columns) < 2:
        return "table"

    # Respect explicit chart requests except table; table is often over-selected by LLM.
    if requested in {"bar", "line", "area", "pie", "scatter"}:
        return requested

    numeric_cols = [c for c in result_df.columns if pd.api.types.is_numeric_dtype(result_df[c])]
    non_numeric_cols = [c for c in result_df.columns if c not in numeric_cols]

    if len(numeric_cols) >= 2:
        return "scatter"
    if len(numeric_cols) >= 1 and len(non_numeric_cols) >= 1:
        if len(result_df) <= 8:
            return "pie"
        if len(result_df) <= 12:
            return "bar"
        return "line"
    return "table"


def pick_axes(result_df: pd.DataFrame, x_axis: str | None, y_axis: str | None) -> Tuple[str | None, str | None]:
    if result_df.empty:
        return None, None

    cols = list(result_df.columns)
    numeric_cols = [c for c in cols if pd.api.types.is_numeric_dtype(result_df[c])]

    if x_axis not in cols:
        x_axis = cols[0]
    if y_axis not in cols:
        y_axis = numeric_cols[0] if numeric_cols else (cols[1] if len(cols) > 1 else cols[0])

    return x_axis, y_axis


def render_chart(result_df: pd.DataFrame, chart_type: str, x_axis: str | None, y_axis: str | None) -> None:
    if result_df.empty:
        st.info("No rows returned for this question.")
        return

    x_axis, y_axis = pick_axes(result_df, x_axis, y_axis)
    if not x_axis or not y_axis:
        st.dataframe(result_df, width="stretch")
        return

    plot_df = result_df[[x_axis, y_axis]].dropna().copy()
    if plot_df.empty:
        st.dataframe(result_df, width="stretch")
        return

    if chart_type == "bar":
        st.bar_chart(plot_df.set_index(x_axis)[y_axis])
        return
    if chart_type == "line":
        st.line_chart(plot_df.set_index(x_axis)[y_axis])
        return
    if chart_type == "area":
        st.area_chart(plot_df.set_index(x_axis)[y_axis])
        return
    if chart_type == "scatter":
        st.scatter_chart(plot_df, x=x_axis, y=y_axis)
        return
    if chart_type == "pie":
        pie = (
            alt.Chart(plot_df)
            .mark_arc()
            .encode(
                theta=alt.Theta(field=y_axis, type="quantitative"), 
                color=alt.Color(field=x_axis, type="nominal")
            )
        )
        st.altair_chart(pie, width="stretch")
        return

    st.dataframe(result_df, width="stretch")

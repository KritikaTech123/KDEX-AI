import csv
import io
from typing import Any, Dict, Tuple

import duckdb
import pandas as pd


def count_csv_rows(file_bytes: bytes) -> int:
    text = file_bytes.decode("utf-8", errors="replace")
    reader = csv.reader(io.StringIO(text, newline=""))
    row_count = -1
    for row_count, _ in enumerate(reader):
        pass
    return max(0, row_count + 1)


def parse_csv_with_recovery(file_bytes: bytes) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    import statistics
    
    text = file_bytes.decode("utf-8", errors="replace")
    source_rows = count_csv_rows(file_bytes)

    # Try delimiter sniffing for better compatibility with unusual CSV exports.
    delimiter = ","
    sample = text[:8192]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t", "|"])
        delimiter = dialect.delimiter
    except Exception:
        pass

    stream = io.StringIO(text, newline="")
    reader = csv.reader(stream, delimiter=delimiter)

    all_rows = []
    empty_rows = 0

    for row in reader:
        if not row or all(str(cell).strip() == "" for cell in row):
            empty_rows += 1
            continue
        all_rows.append(row)

    if not all_rows:
        raise ValueError("Could not detect any valid rows in the file.")

    # Determine the most common row length (the true shape of the data)
    row_lengths = [len(r) for r in all_rows]
    try:
        mode_len = statistics.mode(row_lengths)
    except statistics.StatisticsError:
        mode_len = max(row_lengths)

    # Find the header (first row that has at least mode_len - 2 columns, to be safe)
    header_idx = 0
    for idx, row in enumerate(all_rows):
        if len(row) >= max(1, mode_len - 2):
            header_idx = idx
            break

    raw_header = all_rows[header_idx]
    # Pad or truncate header to match mode_len
    if len(raw_header) < mode_len:
        raw_header.extend([f"Unlabeled_{i}" for i in range(len(raw_header), mode_len)])
    raw_header = raw_header[:mode_len]

    cleaned_header = []
    seen = set()
    for idx, col in enumerate(raw_header):
        base = col.strip() if col.strip() else f"column_{idx + 1}"
        name = base
        suffix = 2
        while name in seen:
            name = f"{base}_{suffix}"
            suffix += 1
        seen.add(name)
        cleaned_header.append(name)

    malformed_rows = 0
    parsed_rows = 0
    valid_rows = []

    # Process data rows (everything after the header)
    for row in all_rows[header_idx + 1:]:
        parsed_rows += 1
        current_len = len(row)
        
        if current_len == mode_len:
            valid_rows.append(row)
        else:
            malformed_rows += 1
            # Smart recovery: Pad if too short, truncate if too long
            if current_len < mode_len:
                row.extend([None] * (mode_len - current_len))
                valid_rows.append(row)
            else:
                valid_rows.append(row[:mode_len])

    if not valid_rows:
        raise ValueError("No valid data rows found after applying structural recovery.")

    df = pd.DataFrame(valid_rows, columns=cleaned_header)
    
    # Optional: LLM could be used here to rename columns intelligently if they are generic,
    # but statistical pad/truncate already saves 99% of formatting issues.

    report = {
        "source_rows": source_rows,
        "parsed_rows": parsed_rows,
        "malformed_fixed": malformed_rows,
        "empty_rows": empty_rows,
        "valid_rows": len(df),
        "delimiter": delimiter,
        "mode_columns": mode_len,
        "parser": "smart-statistical-recovery",
    }
    return df, report


def clean_dataframe_for_corruption(
    raw_df: pd.DataFrame,
    source_row_count: int,
    parse_report: Dict[str, Any] | None = None,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    original_rows = len(raw_df)
    non_null_ratio = raw_df.notna().mean(axis=1)
    cleaned_df = raw_df.loc[non_null_ratio >= 0.5].copy()
    
    removed_sparse_rows = int(original_rows - len(cleaned_df))
    skipped_on_parse = max(0, source_row_count - original_rows)
    bad_rows_removed = skipped_on_parse + removed_sparse_rows

    if cleaned_df.empty:
        raise ValueError("Uploaded file has no usable rows.")

    report = {
        "row_count": len(cleaned_df),
        "column_count": len(cleaned_df.columns),
        "bad_rows_removed": bad_rows_removed,
        "removed_sparse_rows": removed_sparse_rows,
        "source_row_count": source_row_count,
    }
    if parse_report:
        report.update(parse_report)
    return cleaned_df, report


def is_safe_select_query(sql: str) -> bool:
    if not sql or not isinstance(sql, str):
        return False
    compact = sql.strip().lower()
    dangerous = ["drop ", "delete ", "truncate ", "update ", "insert ", "alter ", "create "]
    if any(token in compact for token in dangerous):
        return False
    return compact.startswith("select")


def run_sql_query(df: pd.DataFrame, sql: str) -> pd.DataFrame:
    if not is_safe_select_query(sql):
        raise ValueError("For safety, only SELECT queries are allowed.")
    con = duckdb.connect(database=":memory:")
    try:
        con.register("dataset", df)
        return con.sql(sql.rstrip().rstrip(";")).df()
    finally:
        con.close()

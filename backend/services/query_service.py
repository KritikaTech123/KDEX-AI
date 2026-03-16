import duckdb
import pandas as pd
import io

def load_csv_to_duckdb(file):
    content = file.file.read()
    df = pd.read_csv(io.BytesIO(content))
    duckdb.sql("DROP TABLE IF EXISTS dataset")
    duckdb.register("dataset", df)
    return df

def extract_schema(df):
    return {
        "columns": list(df.columns),
        "sample_rows": df.head(5).to_dict(orient="records")
    }

def run_sql_query(sql):
    result = duckdb.query(sql).to_df()
    return result.to_dict(orient="records")

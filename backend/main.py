from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.query_service import load_csv_to_duckdb, extract_schema, run_sql_query
from services.gemini_service import generate_sql_from_prompt
from pydantic import BaseModel
import pandas as pd
import duckdb
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    prompt: str

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    try:
        df = await load_csv_to_duckdb(file)
        schema = extract_schema(df)
        return schema
    except Exception as e:
        import traceback
        print("[UPLOAD ERROR]", traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")

@app.post("/query")
async def query_data(req: QueryRequest):
    import traceback
    try:
        # Get schema and sample rows
        df = duckdb.query("SELECT * FROM dataset LIMIT 5").to_df()
        columns = list(df.columns)
        sample_rows = df.to_dict(orient="records")
        # Call Groq to get SQL and chart config
        try:
            groq_resp = generate_sql_from_prompt(columns, sample_rows, req.prompt)
        except Exception as llm_error:
            print("[LLM ERROR]", traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"AI (Groq) error: {str(llm_error)}")
        sql = groq_resp.get("sql")
        chart_type = groq_resp.get("chart_type")
        x_axis = groq_resp.get("x_axis")
        y_axis = groq_resp.get("y_axis")
        if not sql or not chart_type or not x_axis or not y_axis:
            print("[LLM RESPONSE ERROR]", groq_resp)
            raise HTTPException(status_code=400, detail="AI did not return a valid chart configuration.")
        # Run SQL
        try:
            data = run_sql_query(sql)
        except Exception as sql_error:
            print("[SQL ERROR]", traceback.format_exc())
            raise HTTPException(status_code=400, detail=f"SQL error: {str(sql_error)}\nSQL: {sql}")
        if not isinstance(data, list) or len(data) == 0:
            print("[DATA ERROR]", data)
            raise HTTPException(status_code=400, detail="Query returned no data or invalid data format.")
        return {"chart_type": chart_type, "data": data, "x_axis": x_axis, "y_axis": y_axis}
    except HTTPException as he:
        raise he
    except Exception as e:
        print("[QUERY ERROR]", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

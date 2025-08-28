from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pydantic import BaseModel
from db import engine, generate_data

app = FastAPI()

# Generate data
generate_data()

# Allow requests from React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Backend is running!"}

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
def run_query(request: QueryRequest):
    sql = request.query
    df = pd.read_sql(sql, con=engine)
    return df.to_dict(orient="records")

# SELECT p.patient_id, AVG(r.heart_rate) AS avg_hr FROM patients p JOIN devices d ON p.patient_id = d.patient_id JOIN readings r ON d.device_id = r.device_id GROUP BY p.patient_id

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import init_db

app = FastAPI()

# Initialize database tables
init_db()

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
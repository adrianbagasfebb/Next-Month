from fastapi import FastAPI 
from app.routes import transactions, auth, financial_summary

app = FastAPI(
    title="NextMonth API",
    description="Personal Finance Management API",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(financial_summary.router)
@app.get("/")
def root():
    return {
        "message": "Welcome to NextMonth API!",
        "status": "running",
        }

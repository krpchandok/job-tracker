import os
import psycopg2
from fastapi import FastAPI, include_router
from pydantic import BaseModel

app = FastAPI(title="job-tracker-backend", version="1.0.0")
app.include_router(posts.router)

class HealthResponse(BaseModel):
    status: str
    version: str


@app.get("/health")
async def health_response():
    return HealthResponse(status="ok", version="1.0.0")
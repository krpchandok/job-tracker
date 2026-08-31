import os
import psycopg2
from fastapi import FastAPI
from pydantic import BaseModel
import services.api.crud as posts


app = FastAPI(title="job-tracker-backend", version="1.0.0")

# Include the posts router from the CRUD module
app.include_router(posts.router)


class HealthResponse(BaseModel):
    status: str
    version: str


@app.get("/health")
async def health_response():
    return HealthResponse(status="ok", version="1.0.0")
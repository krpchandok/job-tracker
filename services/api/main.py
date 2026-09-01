import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import services.api.crud as posts
import services.api.db as db_mod
import services.api.models as models_mod
import services.api.mock_data as mock_data


app = FastAPI(title="job-tracker-backend", version="1.0.0")

# Allow the local Vite dev server (and anything else during development) to call the API.
_cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the posts router from the CRUD module
app.include_router(posts.router)


class HealthResponse(BaseModel):
    status: str
    version: str


@app.get("/health")
async def health_response():
    return HealthResponse(status="ok", version="1.0.0")


def _seed_mock_jobs():
    """Insert the fallback mock jobs if the table is empty.

    This guarantees the frontend has something to show even before the
    scraper has run. Set SEED_MOCK_JOBS=0 to disable.
    """
    if os.getenv("SEED_MOCK_JOBS", "1") != "1":
        return
    session = db_mod.SessionLocal()
    try:
        if session.query(models_mod.JobPosting).count() > 0:
            return
        for job in mock_data.MOCK_JOBS:
            session.add(models_mod.JobPosting(**job))
        session.commit()
        print(f"Seeded {len(mock_data.MOCK_JOBS)} mock jobs")
    finally:
        session.close()


@app.on_event("startup")
def on_startup():
    # Ensure DB tables are created for development (replace with migrations in production)
    db_mod.Base.metadata.create_all(bind=db_mod.engine)
    _seed_mock_jobs()

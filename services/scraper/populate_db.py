"""Scrape public job boards (Greenhouse / Lever) and push postings into the API.

Usage:
    python -m services.scraper.populate_db stripe airbnb databricks
    # or set companies via env (comma separated):
    AGG_COMPANIES=stripe,airbnb python -m services.scraper.populate_db

Config:
    API_URL          base URL of the backend      (default http://localhost:8000)
    AGG_COMPANIES    comma-separated board tokens  (used when no CLI args given)
    AGG_FILTER       "1" to keep only tech internships, "0" for every posting
                     (default "1")
"""

import os
import sys
import pathlib

import requests

# Make `import services...` work when this file is run as a script from anywhere.
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.scraper.aggregator import JobAggregator  # noqa: E402

API_URL = os.getenv("API_URL", "http://localhost:8000")

DEFAULT_COMPANIES = [
    "stripe",
    "airbnb",
    "databricks",
    "gitlab",
    "cloudflare",
]


def post_job(job: dict) -> bool:
    url = f"{API_URL}/posts/jobs"
    try:
        resp = requests.post(url, json=job, timeout=15)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"  ! failed to post {job.get('title')!r}: {e}")
        return False


def normalize(job: dict, company: str) -> dict:
    return {
        "title": job.get("title") or "Untitled role",
        "company": job.get("company") or company,
        "status": job.get("status") or "SAVED",
        "term": job.get("term"),  # may be None; the API accepts that
        "required_skills": job.get("required_skills") or [],
        "url": job.get("url"),
        "location": job.get("location"),
        "source": job.get("source"),
    }


def companies_from_config() -> list[str]:
    if len(sys.argv) > 1:
        return sys.argv[1:]
    env = os.getenv("AGG_COMPANIES", "").strip()
    if env:
        return [c.strip() for c in env.split(",") if c.strip()]
    return DEFAULT_COMPANIES


def main() -> None:
    companies = companies_from_config()
    use_filter = os.getenv("AGG_FILTER", "1") == "1"

    total_found = 0
    total_posted = 0

    for company in companies:
        agg = JobAggregator(company)
        if use_filter:
            # internships / co-ops only — no fallback to full-time roles
            jobs = agg.fetch_filtered_jobs(require_internship=True)
        else:
            jobs = agg.fetch_all_jobs()
        print(f"{company}: found {len(jobs)} jobs")
        total_found += len(jobs)
        for job in jobs:
            if post_job(normalize(job, company)):
                total_posted += 1

    print(f"\nDone. Scraped {total_found} jobs, posted {total_posted} to {API_URL}.")
    if total_posted == 0:
        print(
            "No jobs were posted. The API still serves the built-in mock jobs "
            "so the frontend will not be empty."
        )


if __name__ == "__main__":
    main()

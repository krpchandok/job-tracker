import os
import time
import json
import requests
from aggregator import JobAggregator

API_URL = os.getenv("API_URL", "http://localhost:8000")


def post_job(payload: dict) -> dict:
    url = f"{API_URL}/posts/jobs"
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Failed to post job {payload.get('title')}: {e}")
        return {}


if __name__ == "__main__":
    company = os.getenv("AGG_COMPANY", "")
    if not company:
        raise SystemExit("AGG_COMPANY env var is required, e.g. AGG_COMPANY=stripe")

    aggregator = JobAggregator(company=company)
    jobs = aggregator.fetch_all_jobs()

    print(f"Fetched {len(jobs)} jobs from aggregator")

    for j in jobs:
        payload = {
            "title": j.get("title") or "",
            "company": j.get("company") or "",
            "status": j.get("status") or "SAVED",
            "term": j.get("term") or "winter",
            "required_skills": j.get("required_skills") or [],
            "url": j.get("url"),
            "location": j.get("location"),
            "source": j.get("source"),
        }
        result = post_job(payload)
        print("Result:", result)
        time.sleep(0.2)

    print("Done.")
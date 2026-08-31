import urllib.request
import json

class JobAggregator:
    def __init__(self, company: str):
        self.company = company
        self.endpoints = {
            "greenhouse": f"https://boards-api.greenhouse.io/v1/boards/{self.company}/jobs",
            "lever": f"https://api.lever.co/v0/postings/{self.company}?mode=json",
        }

    def _fetch_json(self, url: str) -> dict:
        """Helper to safely make HTTP requests and parse JSON."""
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            print(f"Error fetching from {url}: {e}")
            return {}

    def fetch_all_jobs(self) -> list:
        """Fetches from all sources and compiles a standardized list[dict]."""
        unified_jobs = []

        # 1. Greenhouse
        gh_data = self._fetch_json(self.endpoints["greenhouse"])
        for job in gh_data.get("jobs", []):
            unified_jobs.append({
                "title": job.get("title"),
                "company": self.company,
                "status": "SAVED",
                "term": None,
                "required_skills": [],
                "location": job.get("location", {}).get("name"),
                "url": job.get("absolute_url"),
                "source": "Greenhouse",
            })

        # 2. Lever
        lever_data = self._fetch_json(self.endpoints["lever"])
        if isinstance(lever_data, list):
            for job in lever_data:
                unified_jobs.append({
                    "title": job.get("text") or job.get("position"),
                    "company": self.company,
                    "status": "SAVED",
                    "term": None,
                    "required_skills": [],
                    "location": job.get("categories", {}).get("location"),
                    "url": job.get("hostedUrl"),
                    "source": "Lever",
                })

        return unified_jobs
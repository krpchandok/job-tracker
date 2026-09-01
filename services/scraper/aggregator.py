import urllib.request
import json
import html
import re

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

    @staticmethod
    def _guess_term(title: str):
        """Best-effort season extraction from a job title (winter/summer/fall)."""
        if not title:
            return None
        t = title.lower()
        if "summer" in t:
            return "summer"
        if "winter" in t:
            return "winter"
        if "fall" in t or "autumn" in t:
            return "fall"
        return None

    def fetch_all_jobs(self) -> list:
        """Fetches from all sources and compiles a standardized list[dict]."""
        unified_jobs = []
        # 1. Greenhouse - try various board token candidates
        gh_jobs, gh_token = self._fetch_greenhouse_jobs_with_candidates()
        if gh_jobs:
            for job in gh_jobs:
                # job from list may be abbreviated; normalize available fields
                unified_jobs.append({
                    "title": job.get("title"),
                    "company": self.company,
                    "status": "SAVED",
                    "term": self._guess_term(job.get("title")),
                    "required_skills": [],
                    "location": (job.get("location") or {}).get("name") if isinstance(job.get("location"), dict) else job.get("location"),
                    "url": job.get("absolute_url") or job.get("absoluteUrl"),
                    "source": f"Greenhouse:{gh_token}" if gh_token else "Greenhouse",
                })

        # 2. Lever
        lever_data = self._fetch_json(self.endpoints["lever"])
        if isinstance(lever_data, list):
            for job in lever_data:
                unified_jobs.append({
                    "title": job.get("text") or job.get("position"),
                    "company": self.company,
                    "status": "SAVED",
                    "term": self._guess_term(job.get("text") or job.get("position")),
                    "required_skills": [],
                    "location": job.get("categories", {}).get("location"),
                    "url": job.get("hostedUrl"),
                    "source": "Lever",
                })

        return unified_jobs

    def _generate_greenhouse_candidates(self) -> list:
        """Return a list of possible Greenhouse board tokens derived from company name."""
        name = self.company or ""
        candidates = []
        s = name.strip()
        candidates.append(s)
        candidates.append(s.lower())
        candidates.append(s.replace(" ", "-"))
        candidates.append(s.replace(" ", ""))
        candidates.append(s.replace(".", ""))
        candidates.append(s.split()[0] if s.split() else s)
        # also try common short forms
        candidates = [c for c in dict.fromkeys(candidates) if c]
        return candidates

    def _fetch_greenhouse_jobs_with_candidates(self) -> tuple[list, str]:
        """Try multiple greenhouse board token candidates and return (jobs, used_token).

        Returns empty list and None if none succeed.
        """
        base = self.endpoints.get("greenhouse")
        if not base:
            # default playground endpoint when not configured
            base = "https://boards-api.greenhouse.io/v1/boards"

        candidates = self._generate_greenhouse_candidates()
        for cand in candidates:
            url = f"https://boards-api.greenhouse.io/v1/boards/{cand}/jobs"
            data = self._fetch_json(url)
            if isinstance(data, dict) and data.get("jobs"):
                return data.get("jobs"), cand
        # last attempt: try the configured endpoint if it's already a full URL
        try:
            data = self._fetch_json(self.endpoints.get("greenhouse", ""))
            if isinstance(data, dict) and data.get("jobs"):
                return data.get("jobs"), None
        except Exception:
            pass

        return [], None

    def fetch_filtered_jobs(self, require_internship: bool = True) -> list:
        """Return tech-related roles, optionally restricted to internships/co-ops.

        Filtering is heuristic-based on the job title. With
        ``require_internship=True`` (the default) a posting must look like both an
        internship *and* a tech role; with it ``False`` any tech role is kept,
        which is a useful fallback for boards that publish no internships.
        """
        jobs = self.fetch_all_jobs()
        filtered = []
        internship_keywords = ["intern", "internship", "co-op", "coop", "co op", "apprentice"]
        tech_keywords = [
            "software",
            "engineer",
            "developer",
            "swe",
            "machine learning",
            "ml",
            "ai",
            "data",
            "backend",
            "frontend",
            "full stack",
            "fullstack",
            "site reliability",
            "sre",
            "devops",
            "platform",
            "infrastructure",
            "security",
        ]

        def matches_any(text, keywords):
            if not text:
                return False
            text_l = text.lower()
            # word-boundary match so "intern" doesn't fire on "international"
            return any(re.search(r"\b" + re.escape(k) + r"\b", text_l) for k in keywords)

        for job in jobs:
            title = job.get("title") or ""
            categories = job.get("source", "")

            is_intern = matches_any(title, internship_keywords)
            is_tech = matches_any(title, tech_keywords)

            if is_tech and (is_intern or not require_internship):
                filtered.append(job)

        return filtered

    def fetch_job_details(self, job_id: int, include_questions: bool = False) -> dict:
        """Fetch the full job payload for a Greenhouse job and return parsed dict.

        Uses the Greenhouse boards API: /v1/boards/{board_token}/jobs/{job_id}
        Set `include_questions=True` to request application fields.
        """
        base = self.endpoints.get("greenhouse")
        if not base:
            return {}

        # base is like .../boards/{company}/jobs
        url = f"{base}/{job_id}"
        if include_questions:
            url = f"{url}?questions=true"

        data = self._fetch_json(url)
        if not data:
            return {}

        return self.parse_greenhouse_job(data)

    def parse_greenhouse_job(self, data: dict) -> dict:
        """Normalize a Greenhouse job JSON (single job) to our internal job dict.

        Returns fields compatible with `JobBase`: title, company, status, term,
        required_skills, url, location, source, plus `description` from content.
        """
        title = data.get("title")
        company_name = data.get("company_name") or self.company
        location = None
        if isinstance(data.get("location"), dict):
            location = data.get("location").get("name")

        # unescape HTML entities in content
        raw_content = data.get("content") or ""
        description = html.unescape(raw_content)

        return {
            "title": title,
            "company": company_name,
            "status": "SAVED",
            "term": None,
            "required_skills": [],
            "url": data.get("absolute_url"),
            "location": location,
            "source": "Greenhouse",
            "description": description,
        }
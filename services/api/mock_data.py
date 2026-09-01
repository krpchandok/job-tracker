"""Fallback job data used to seed the database when the scraper finds nothing.

Values here must be valid for the enums in ``services.api.models``:
``status`` is one of SAVED/APPLIED/INTERVIEWED/OFFER/REJECTED and ``term`` is
one of winter/summer/fall (or ``None``).
"""

MOCK_JOBS = [
    {
        "title": "Software Engineering Intern",
        "company": "Acme Corp",
        "status": "SAVED",
        "term": "summer",
        "required_skills": ["Python", "SQL", "APIs"],
        "url": "https://acme.example.com/jobs/123",
        "location": "San Francisco, CA",
        "source": "Mock:acme",
    },
    {
        "title": "Frontend Engineer Intern",
        "company": "Beta Labs",
        "status": "SAVED",
        "term": None,
        "required_skills": ["React", "TypeScript", "CSS"],
        "url": "https://beta.example.com/careers/fe-1",
        "location": "Remote",
        "source": "Mock:beta",
    },
    {
        "title": "Data Science Intern",
        "company": "Gamma Analytics",
        "status": "SAVED",
        "term": "fall",
        "required_skills": ["Python", "pandas", "SQL"],
        "url": "https://gamma.example.com/jobs/45",
        "location": "New York, NY",
        "source": "Mock:gamma",
    },
]

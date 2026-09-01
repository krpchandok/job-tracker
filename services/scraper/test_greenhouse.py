import json
from services.scraper.aggregator import JobAggregator


sample = {
    "id": 44444,
    "title": "Product Engineer",
    "company_name": "Greenhouse",
    "first_published": "2013-08-01T20:00:00Z",
    "updated_at": "2013-07-02T19:39:23Z",
    "application_deadline": "2026-08-01T20:00:00Z",
    "requisition_id": "50",
    "location": {"name": "San Francisco, CA"},
    "content": "This is the job description. &amp;lt;p&amp;gt;Any HTML included through the hosted job application editor will be automatically converted into corresponding HTML entities.&amp;lt;/p&amp;gt;",
    "absolute_url": "http://your.co/careers?gh_jid=444444",
    "language": "en",
    "internal_job_id": 55555,
    "include_ai_disclaimer": True,
    "ai_disclaimer": "<p>We use Greenhouse’s AI-powered Talent Matching tool to compare your application against our job requirements.</p>",
    "ai_opt_out_request_url": "https://app.greenhouse.io/job_post/55555/ai_opt_out",
    "location_questions": [],
    "questions": [],
    "metadata": [{"id": 12345, "name": "Field Name", "value_type": "text", "value": "Some value"}],
    "data_compliance": [
        {
            "type": "gdpr",
            "requires_consent": True,
            "requires_processing_consent": True,
            "requires_retention_consent": True,
            "retention_period": 12345,
        }
    ],
    "pay_input_ranges": [
        {
            "min_cents": 5000000,
            "max_cents": 7500000,
            "currency_type": "USD",
            "title": "NYC Salary Range",
            "blurb": "In order to provide transparency...",
        }
    ],
}


def run_test():
    agg = JobAggregator("example")
    parsed = agg.parse_greenhouse_job(sample)
    print(json.dumps(parsed, indent=2))


if __name__ == "__main__":
    run_test()

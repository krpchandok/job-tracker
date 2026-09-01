# job-tracker

FastAPI + Postgres backend, a scraper that pulls postings from public job
boards (Greenhouse / Lever), and a Vite + React frontend.

## Run the backend

```bash
docker compose up -d --build db backend
# API on http://localhost:8000  (docs at /docs)
```

On first boot the API creates its tables and seeds a few mock jobs so the
frontend is never empty. Disable that with `SEED_MOCK_JOBS=0`.

## Fill the database from real job boards

```bash
# scrape the default company list (see docker-compose.yml -> AGG_COMPANIES)
docker compose --profile seed run --rm scraper

# or pass Greenhouse/Lever board tokens explicitly
docker compose --profile seed run --rm scraper stripe gitlab databricks airbnb
```

The scraper keeps **tech internships / co-ops only** (`AGG_FILTER=1`, the
default). Boards with no open internships simply contribute nothing — set
`AGG_FILTER=0` to take every posting instead. The season (winter/summer/fall)
is guessed from the title. Postings already in the DB (matched by URL) are
skipped, so it is safe to re-run, and if a board can't be reached the run
continues.

Many large employers (Microsoft, NVIDIA, Google, …) don't use Greenhouse or
Lever, so they can't be scraped here — add those postings by hand from the
frontend's **Add job** tab (or `POST /posts/jobs`).

Env vars for the `scraper` service:

| var             | meaning                                            |
| --------------- | ------------------------------------------------- |
| `AGG_COMPANIES` | comma-separated board tokens (used if no CLI args) |
| `AGG_FILTER`    | `1` = internships/tech only, `0` = every posting   |
| `API_URL`       | backend base URL (default `http://backend:8000`)   |

## Run the frontend

```bash
cd services/frontend
npm install
npm run dev
# http://localhost:5173  — reads VITE_API_URL, default http://localhost:8000
```

Layout: the left pane is a scrollable job list (each card has a delete
button); the right pane has three tabs — **Add job** (manual entry),
**Filter** (search + status / term / company / source), and **Resumes**
(placeholder, see below).

## API

| method   | path                  | notes                                             |
| -------- | --------------------- | ------------------------------------------------- |
| `GET`    | `/posts/jobs`         | filters: `q`, `status`, `term`, `company`, `source` |
| `POST`   | `/posts/jobs`         | manual add — only `title` + `company` required     |
| `PATCH`  | `/posts/jobs/{id}`    | partial update                                     |
| `DELETE` | `/posts/jobs/{id}`    | remove a posting                                   |

## Resume storage (not built yet)

The **Resumes** tab is a stub. The plan is object storage in the cloud:
upload resume PDFs to Cloudflare R2 or AWS S3, store metadata (label, target
role, created date) in Postgres, and list / download them from that tab.

## Reset the database

```bash
docker compose down -v && docker compose up -d --build db backend
```

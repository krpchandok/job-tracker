import { useCallback, useEffect, useMemo, useState } from "react";
import {
  createJob,
  deleteJob,
  fetchJobs,
  STATUSES,
  TERMS,
  type Job,
  type JobFilters,
  type NewJob,
  type Status,
  type Term,
} from "./api";
import "./jobs.css";

/* ---------------- Job list (left pane) ---------------- */

function StatusBadge({ status }: { status: Status }) {
  return <span className={`badge status-${status}`}>{status.toLowerCase()}</span>;
}

function JobCard({ job, onDelete }: { job: Job; onDelete: (id: number) => void }) {
  return (
    <article className="job-card">
      <div className="job-card-top">
        <h3 className="job-title">
          {job.url ? (
            <a href={job.url} target="_blank" rel="noreferrer">
              {job.title}
            </a>
          ) : (
            job.title
          )}
        </h3>
        <button
          className="icon-btn"
          title="Delete posting"
          onClick={() => onDelete(job.id)}
        >
          ✕
        </button>
      </div>

      <div className="job-company">{job.company}</div>

      <div className="job-meta">
        <StatusBadge status={job.status} />
        {job.term && <span className="badge term">{job.term}</span>}
        <span className="job-loc">{job.location || "Location N/A"}</span>
      </div>

      {job.required_skills.length > 0 && (
        <p className="job-skills">
          {job.required_skills.slice(0, 6).map((s) => (
            <span key={s} className="chip">
              {s}
            </span>
          ))}
        </p>
      )}

      <div className="job-source">{job.source || "unknown source"}</div>
    </article>
  );
}

/* ---------------- Add job (right pane tab) ---------------- */

const EMPTY_FORM = {
  title: "",
  company: "",
  status: "SAVED" as Status,
  term: "" as "" | Term,
  location: "",
  url: "",
  required_skills: "",
  source: "",
};

function AddJobForm({ onCreated }: { onCreated: (job: Job) => void }) {
  const [form, setForm] = useState({ ...EMPTY_FORM });
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ kind: "ok" | "err"; text: string } | null>(
    null
  );

  const set = <K extends keyof typeof form>(key: K, value: (typeof form)[K]) =>
    setForm((f) => ({ ...f, [key]: value }));

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setMsg(null);
    if (!form.title.trim() || !form.company.trim()) {
      setMsg({ kind: "err", text: "Title and company are required." });
      return;
    }
    const payload: NewJob = {
      title: form.title.trim(),
      company: form.company.trim(),
      status: form.status,
      term: form.term ? (form.term as Term) : null,
      required_skills: form.required_skills
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
      url: form.url.trim() || null,
      location: form.location.trim() || null,
      source: form.source.trim() || "manual",
    };
    setBusy(true);
    try {
      const job = await createJob(payload);
      onCreated(job);
      setForm({ ...EMPTY_FORM });
      setMsg({ kind: "ok", text: `Added “${job.title}”.` });
    } catch (err) {
      setMsg({
        kind: "err",
        text: err instanceof Error ? err.message : "Failed to add job.",
      });
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="form" onSubmit={submit}>
      <label className="field">
        <span>Title *</span>
        <input
          value={form.title}
          onChange={(e) => set("title", e.target.value)}
          placeholder="Software Engineering Intern"
        />
      </label>

      <label className="field">
        <span>Company *</span>
        <input
          value={form.company}
          onChange={(e) => set("company", e.target.value)}
          placeholder="Acme Corp"
        />
      </label>

      <div className="field-row">
        <label className="field">
          <span>Status</span>
          <select
            value={form.status}
            onChange={(e) => set("status", e.target.value as Status)}
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s.toLowerCase()}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Term</span>
          <select
            value={form.term}
            onChange={(e) => set("term", e.target.value as "" | Term)}
          >
            <option value="">—</option>
            {TERMS.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>
      </div>

      <label className="field">
        <span>Location</span>
        <input
          value={form.location}
          onChange={(e) => set("location", e.target.value)}
          placeholder="Remote / San Francisco, CA"
        />
      </label>

      <label className="field">
        <span>URL</span>
        <input
          value={form.url}
          onChange={(e) => set("url", e.target.value)}
          placeholder="https://…"
        />
      </label>

      <label className="field">
        <span>Required skills (comma separated)</span>
        <input
          value={form.required_skills}
          onChange={(e) => set("required_skills", e.target.value)}
          placeholder="Python, SQL, React"
        />
      </label>

      <label className="field">
        <span>Source</span>
        <input
          value={form.source}
          onChange={(e) => set("source", e.target.value)}
          placeholder="manual"
        />
      </label>

      <button className="btn primary" disabled={busy} type="submit">
        {busy ? "Adding…" : "Add job"}
      </button>

      {msg && <p className={`form-msg ${msg.kind}`}>{msg.text}</p>}
    </form>
  );
}

/* ---------------- Filter (right pane tab) ---------------- */

function FilterPanel({
  filters,
  onApply,
}: {
  filters: JobFilters;
  onApply: (f: JobFilters) => void;
}) {
  const [draft, setDraft] = useState<JobFilters>(filters);
  useEffect(() => setDraft(filters), [filters]);

  const set = (key: keyof JobFilters, value: string) =>
    setDraft((d) => ({ ...d, [key]: value }));

  return (
    <form
      className="form"
      onSubmit={(e) => {
        e.preventDefault();
        onApply(draft);
      }}
    >
      <label className="field">
        <span>Search (title / company)</span>
        <input
          value={draft.q ?? ""}
          onChange={(e) => set("q", e.target.value)}
          placeholder="intern, backend, …"
        />
      </label>

      <div className="field-row">
        <label className="field">
          <span>Status</span>
          <select
            value={draft.status ?? ""}
            onChange={(e) => set("status", e.target.value)}
          >
            <option value="">any</option>
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s.toLowerCase()}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Term</span>
          <select
            value={draft.term ?? ""}
            onChange={(e) => set("term", e.target.value)}
          >
            <option value="">any</option>
            {TERMS.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>
      </div>

      <label className="field">
        <span>Company</span>
        <input
          value={draft.company ?? ""}
          onChange={(e) => set("company", e.target.value)}
          placeholder="stripe"
        />
      </label>

      <label className="field">
        <span>Source</span>
        <input
          value={draft.source ?? ""}
          onChange={(e) => set("source", e.target.value)}
          placeholder="Greenhouse / manual"
        />
      </label>

      <div className="field-row">
        <button className="btn primary" type="submit">
          Apply filters
        </button>
        <button
          className="btn"
          type="button"
          onClick={() => {
            setDraft({});
            onApply({});
          }}
        >
          Clear
        </button>
      </div>
    </form>
  );
}

/* ---------------- Resumes (placeholder tab) ---------------- */

function ResumesPanel() {
  return (
    <div className="placeholder">
      <h3>Resume versions</h3>
      <p>
        Not built yet — this is where multiple resume versions will live so you
        can attach the right one per application.
      </p>
      <p>
        Planned: upload PDFs to cloud object storage (e.g. Cloudflare R2 or AWS
        S3), keep metadata (label, created date, target role) in Postgres, and
        download / preview them here.
      </p>
    </div>
  );
}

/* ---------------- App shell ---------------- */

type Tab = "add" | "filter" | "resumes";

export default function App() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<JobFilters>({});
  const [tab, setTab] = useState<Tab>("add");

  const load = useCallback((f: JobFilters) => {
    setLoading(true);
    setError(null);
    fetchJobs(f)
      .then(setJobs)
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "Failed to load jobs")
      )
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load(filters);
  }, [filters, load]);

  const activeFilterCount = useMemo(
    () => Object.values(filters).filter((v) => v && String(v).trim()).length,
    [filters]
  );

  function handleDelete(id: number) {
    const prev = jobs;
    setJobs((js) => js.filter((j) => j.id !== id));
    deleteJob(id).catch(() => setJobs(prev));
  }

  return (
    <div className="layout">
      <section className="pane pane-left">
        <header className="pane-header">
          <h1>Jobs</h1>
          <span className="count">
            {loading ? "…" : `${jobs.length}`}
            {activeFilterCount > 0 && !loading && (
              <span className="count-filtered"> filtered</span>
            )}
          </span>
        </header>

        <div className="job-list">
          {error && <div className="state err">{error}</div>}
          {!error && loading && <div className="state">Loading…</div>}
          {!error && !loading && jobs.length === 0 && (
            <div className="state">
              No jobs match. Add one on the right, or run the scraper:
              <code>docker compose --profile seed run --rm scraper</code>
            </div>
          )}
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} onDelete={handleDelete} />
          ))}
        </div>
      </section>

      <section className="pane pane-right">
        <nav className="tabs">
          <button
            className={tab === "add" ? "tab active" : "tab"}
            onClick={() => setTab("add")}
          >
            Add job
          </button>
          <button
            className={tab === "filter" ? "tab active" : "tab"}
            onClick={() => setTab("filter")}
          >
            Filter{activeFilterCount > 0 ? ` (${activeFilterCount})` : ""}
          </button>
          <button
            className={tab === "resumes" ? "tab active" : "tab"}
            onClick={() => setTab("resumes")}
          >
            Resumes
          </button>
        </nav>

        <div className="tab-panel">
          {tab === "add" && (
            <AddJobForm onCreated={(job) => setJobs((js) => [job, ...js])} />
          )}
          {tab === "filter" && (
            <FilterPanel filters={filters} onApply={setFilters} />
          )}
          {tab === "resumes" && <ResumesPanel />}
        </div>
      </section>
    </div>
  );
}

const API_URL =
  (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000";

export const STATUSES = [
  "SAVED",
  "APPLIED",
  "INTERVIEWED",
  "OFFER",
  "REJECTED",
] as const;
export const TERMS = ["winter", "summer", "fall"] as const;

export type Status = (typeof STATUSES)[number];
export type Term = (typeof TERMS)[number];

export type Job = {
  id: number;
  title: string;
  company: string;
  status: Status;
  term: Term | null;
  required_skills: string[];
  url: string | null;
  location: string | null;
  source: string | null;
};

export type JobFilters = {
  q?: string;
  status?: string;
  term?: string;
  company?: string;
  source?: string;
};

export type NewJob = {
  title: string;
  company: string;
  status: Status;
  term: Term | null;
  required_skills: string[];
  url: string | null;
  location: string | null;
  source: string | null;
};

export async function fetchJobs(filters: JobFilters = {}): Promise<Job[]> {
  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(filters)) {
    if (v && v.trim()) params.set(k, v.trim());
  }
  const qs = params.toString();
  const res = await fetch(`${API_URL}/posts/jobs${qs ? `?${qs}` : ""}`);
  if (!res.ok) throw new Error(`Failed to fetch jobs (${res.status})`);
  return res.json();
}

export async function createJob(job: NewJob): Promise<Job> {
  const res = await fetch(`${API_URL}/posts/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(job),
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`Failed to create job (${res.status}) ${detail}`);
  }
  return res.json();
}

export async function deleteJob(id: number): Promise<void> {
  const res = await fetch(`${API_URL}/posts/jobs/${id}`, { method: "DELETE" });
  if (!res.ok && res.status !== 204) {
    throw new Error(`Failed to delete job (${res.status})`);
  }
}

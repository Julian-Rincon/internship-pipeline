"use client";

import Link from "next/link";
import { FormEvent, useMemo, useState } from "react";
import {
  createApplicationFromJobPosting,
  linkJobPostingCompany,
  type Company,
  type JobPosting,
  type JobPostingApplicationPayload,
  type User
} from "../../lib/api";

const applicationTypes: JobPostingApplicationPayload["type"][] = [
  "formal",
  "speculative",
  "referral",
  "networking",
  "other"
];
const applicationStatuses: JobPostingApplicationPayload["status"][] = [
  "researching",
  "contacted",
  "responded",
  "interviewing",
  "offer",
  "rejected",
  "paused"
];

function nullableValue(formData: FormData, name: string) {
  const value = formData.get(name)?.toString().trim();
  return value ? value : null;
}

function LinkCompanyForm({ jobPosting, companies }: { jobPosting: JobPosting; companies: Company[] }) {
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const formData = new FormData(event.currentTarget);
    const companyId = formData.get("company_id")?.toString();
    if (!companyId) {
      setError("Select a company first.");
      setIsSubmitting(false);
      return;
    }

    try {
      await linkJobPostingCompany(jobPosting.id, companyId);
      window.location.reload();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Could not link company");
      setIsSubmitting(false);
    }
  }

  return (
    <form className="compact-form" onSubmit={onSubmit}>
      {error ? <p className="notice error">{error}</p> : null}
      <label>
        Company
        <select name="company_id" defaultValue="">
          <option value="">Select company</option>
          {companies.map((company) => (
            <option key={company.id} value={company.id}>
              {company.name}
            </option>
          ))}
        </select>
      </label>
      <button type="submit" disabled={isSubmitting || companies.length === 0}>
        Link company
      </button>
    </form>
  );
}

function CreateApplicationForm({ jobPosting, users }: { jobPosting: JobPosting; users: User[] }) {
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage(null);
    setError(null);
    setIsSubmitting(true);

    const formData = new FormData(event.currentTarget);
    const userId = formData.get("user_id")?.toString();
    if (!userId) {
      setError("Select a user first.");
      setIsSubmitting(false);
      return;
    }

    try {
      const application = await createApplicationFromJobPosting(jobPosting.id, {
        user_id: userId,
        type: formData.get("type")?.toString() as JobPostingApplicationPayload["type"],
        status: formData.get("status")?.toString() as JobPostingApplicationPayload["status"],
        next_action: nullableValue(formData, "next_action"),
        next_action_due: nullableValue(formData, "next_action_due"),
        notes: nullableValue(formData, "notes")
      });
      setMessage(`Application created: ${application.id}`);
      setIsSubmitting(false);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Could not create application");
      setIsSubmitting(false);
    }
  }

  return (
    <details className="edit-details">
      <summary>Create application</summary>
      <form className="form compact-form" onSubmit={onSubmit}>
        {message ? <p className="notice">{message}</p> : null}
        {error ? <p className="notice error">{error}</p> : null}
        <div className="form-grid">
          <label>
            User
            <select name="user_id" defaultValue="">
              <option value="">Select user</option>
              {users.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Type
            <select name="type" defaultValue="formal">
              {applicationTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </label>
          <label>
            Status
            <select name="status" defaultValue="researching">
              {applicationStatuses.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </label>
          <label>
            Next action
            <input name="next_action" />
          </label>
          <label>
            Due date
            <input name="next_action_due" type="date" />
          </label>
        </div>
        <label className="full-width">
          Notes
          <textarea name="notes" />
        </label>
        <button type="submit" disabled={isSubmitting || users.length === 0}>
          Create application
        </button>
      </form>
    </details>
  );
}

export function JobPostingsClient({
  jobPostings,
  companies,
  users
}: {
  jobPostings: JobPosting[];
  companies: Company[];
  users: User[];
}) {
  const [query, setQuery] = useState("");
  const [sourceFilter, setSourceFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const companyById = useMemo(() => new Map(companies.map((company) => [company.id, company])), [companies]);
  const sources = useMemo(
    () => Array.from(new Set(jobPostings.map((jobPosting) => jobPosting.source))).sort(),
    [jobPostings]
  );
  const statuses = useMemo(
    () => Array.from(new Set(jobPostings.map((jobPosting) => jobPosting.status))).sort(),
    [jobPostings]
  );

  const filteredJobPostings = jobPostings.filter((jobPosting) => {
    const matchesQuery = !query || jobPosting.title.toLowerCase().includes(query.trim().toLowerCase());
    return (
      matchesQuery &&
      (!sourceFilter || jobPosting.source === sourceFilter) &&
      (!statusFilter || jobPosting.status === statusFilter)
    );
  });

  return (
    <div className="panel table-wrap" style={{ marginTop: 16 }}>
      <div className="toolbar">
        <label>
          Search title
          <input value={query} onChange={(event) => setQuery(event.target.value)} />
        </label>
        <label>
          Source
          <select value={sourceFilter} onChange={(event) => setSourceFilter(event.target.value)}>
            <option value="">All</option>
            {sources.map((source) => (
              <option key={source} value={source}>
                {source}
              </option>
            ))}
          </select>
        </label>
        <label>
          Status
          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            <option value="">All</option>
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </label>
      </div>

      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>Source</th>
            <th>Location</th>
            <th>Remote</th>
            <th>Status</th>
            <th>Detected</th>
            <th>Company</th>
            <th>URL</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filteredJobPostings.length === 0 ? (
            <tr>
              <td colSpan={9} className="muted">
                No job postings match the current filters.
              </td>
            </tr>
          ) : (
            filteredJobPostings.map((jobPosting) => {
              const company = jobPosting.company_id ? companyById.get(jobPosting.company_id) : null;
              return (
                <tr key={jobPosting.id}>
                  <td>
                    <strong>{jobPosting.title}</strong>
                  </td>
                  <td>{jobPosting.source}</td>
                  <td>{jobPosting.location ?? "-"}</td>
                  <td>{jobPosting.remote === null ? "-" : jobPosting.remote ? "yes" : "no"}</td>
                  <td>{jobPosting.status}</td>
                  <td>{jobPosting.detected_at}</td>
                  <td>
                    {company ? <Link href={`/companies/${company.id}`}>{company.name}</Link> : "-"}
                  </td>
                  <td>
                    <a href={jobPosting.url} target="_blank" rel="noreferrer">
                      Job
                    </a>
                  </td>
                  <td>
                    {company ? (
                      <CreateApplicationForm jobPosting={jobPosting} users={users} />
                    ) : (
                      <LinkCompanyForm jobPosting={jobPosting} companies={companies} />
                    )}
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}

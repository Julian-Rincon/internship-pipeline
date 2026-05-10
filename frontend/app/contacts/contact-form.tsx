"use client";

import { FormEvent, useState } from "react";
import { createContact, type Company, type ContactPayload } from "../../lib/api";

const sources = ["manual", "linkedin", "github", "apollo", "hunter", "arxiv", "other"] as const;
const affinityTypes = ["unknown", "none", "alumni", "colombian", "latino", "recruiter", "engineer"] as const;

function nullableValue(formData: FormData, name: string) {
  const raw = formData.get(name)?.toString().trim();
  return raw ? raw : null;
}

export function ContactForm({ companies }: { companies: Company[] }) {
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const formData = new FormData(event.currentTarget);
    const payload: ContactPayload = {
      company_id: nullableValue(formData, "company_id") ?? "",
      full_name: nullableValue(formData, "full_name") ?? "",
      role: nullableValue(formData, "role"),
      email: nullableValue(formData, "email"),
      linkedin_url: nullableValue(formData, "linkedin_url"),
      github_handle: nullableValue(formData, "github_handle"),
      twitter_handle: nullableValue(formData, "twitter_handle"),
      source: nullableValue(formData, "source") as ContactPayload["source"],
      affinity_type: nullableValue(formData, "affinity_type") as ContactPayload["affinity_type"],
      contacted: formData.get("contacted") === "on"
    };

    try {
      await createContact(payload);
      event.currentTarget.reset();
      window.location.reload();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Could not create contact");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="panel form" onSubmit={onSubmit}>
      <h2>Add manual contact</h2>
      {error ? <p className="notice error">{error}</p> : null}
      {companies.length === 0 ? (
        <p className="notice error">Create a company before adding contacts.</p>
      ) : null}
      <div className="form-grid">
        <label>
          Company
          <select name="company_id" required disabled={companies.length === 0}>
            <option value="">Select company</option>
            {companies.map((company) => (
              <option key={company.id} value={company.id}>
                {company.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Full name
          <input name="full_name" required placeholder="Fictional Contact" />
        </label>
        <label>
          Role
          <input name="role" placeholder="Recruiter, Engineer" />
        </label>
        <label>
          Email
          <input name="email" type="email" placeholder="fictional@example.com" />
        </label>
        <label>
          LinkedIn URL
          <input name="linkedin_url" type="url" />
        </label>
        <label>
          GitHub handle
          <input name="github_handle" />
        </label>
        <label>
          Twitter/X handle
          <input name="twitter_handle" />
        </label>
        <label>
          Source
          <select name="source" defaultValue="manual">
            {sources.map((source) => (
              <option key={source} value={source}>
                {source}
              </option>
            ))}
          </select>
        </label>
        <label>
          Affinity
          <select name="affinity_type" defaultValue="unknown">
            {affinityTypes.map((affinity) => (
              <option key={affinity} value={affinity}>
                {affinity}
              </option>
            ))}
          </select>
        </label>
        <label className="checkbox-label">
          <input name="contacted" type="checkbox" />
          Contacted
        </label>
      </div>
      <button type="submit" disabled={isSubmitting || companies.length === 0}>
        {isSubmitting ? "Creating..." : "Create contact"}
      </button>
    </form>
  );
}


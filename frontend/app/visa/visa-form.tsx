"use client";

import { FormEvent, useState } from "react";
import { createVisaData, type VisaDataPayload } from "../../lib/api";

const internFriendlyOptions = ["unknown", "green", "yellow", "red"] as const;

function nullableValue(formData: FormData, name: string) {
  const raw = formData.get(name)?.toString().trim();
  return raw ? raw : null;
}

export function VisaForm() {
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const formData = new FormData(event.currentTarget);
    const sponsorRaw = formData.get("sponsor_verified")?.toString();
    const payload: VisaDataPayload = {
      company_id: nullableValue(formData, "company_id") ?? "",
      country: nullableValue(formData, "country") ?? "",
      intern_friendly: (nullableValue(formData, "intern_friendly") ?? "unknown") as VisaDataPayload["intern_friendly"],
      visa_type: nullableValue(formData, "visa_type"),
      sponsor_verified: sponsorRaw === "on",
      evidence_url: nullableValue(formData, "evidence_url"),
      notes: nullableValue(formData, "notes"),
      last_verified: nullableValue(formData, "last_verified"),
    };

    try {
      await createVisaData(payload);
      event.currentTarget.reset();
      window.location.reload();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Could not create visa entry");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="panel form" onSubmit={onSubmit}>
      <h2>Add visa entry</h2>
      {error ? <p className="notice error">{error}</p> : null}

      <div className="form-grid">
        <label>
          Company ID
          <input name="company_id" required placeholder="UUID" />
        </label>
        <label>
          Country
          <input name="country" required placeholder="e.g. Germany" />
        </label>
        <label>
          Intern friendly
          <select name="intern_friendly" defaultValue="unknown">
            {internFriendlyOptions.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        </label>
        <label>
          Visa type
          <input name="visa_type" placeholder="e.g. J-1, Praktikantenbewilligung" />
        </label>
        <label>
          Evidence URL
          <input name="evidence_url" type="url" placeholder="https://..." />
        </label>
        <label>
          Last verified
          <input name="last_verified" type="date" />
        </label>
        <label className="checkbox-label">
          <input name="sponsor_verified" type="checkbox" />
          Sponsor verified
        </label>
      </div>
      <label className="full-width">
        Notes
        <textarea name="notes" />
      </label>
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Creating..." : "Add visa entry"}
      </button>
    </form>
  );
}

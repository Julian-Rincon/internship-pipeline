"use client";

import { FormEvent, useState } from "react";
import { createCompany, type CompanyPayload } from "../../lib/api";

const tiers = ["", "A", "B", "C"] as const;
const visaValues = ["unknown", "green", "yellow", "red"] as const;
const statuses = ["active", "paused", "rejected", "won"] as const;

export function CompanyForm() {
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const formData = new FormData(event.currentTarget);
    const value = (name: string) => {
      const raw = formData.get(name)?.toString().trim();
      return raw ? raw : null;
    };

    const payload: CompanyPayload = {
      name: value("name") ?? "",
      domain: value("domain"),
      tier: (value("tier") as CompanyPayload["tier"]) || null,
      country: value("country"),
      region: value("region"),
      careers_url: value("careers_url"),
      ats_type: value("ats_type"),
      visa_friendly_intern: value("visa_friendly_intern") as CompanyPayload["visa_friendly_intern"],
      status: value("status") as CompanyPayload["status"]
    };

    try {
      await createCompany(payload);
      event.currentTarget.reset();
      window.location.reload();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Could not create company");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="panel form" onSubmit={onSubmit}>
      <h2>Add company</h2>
      {error ? <p className="notice error">{error}</p> : null}

      <div className="form-grid">
        <label>
          Name
          <input name="name" required />
        </label>
        <label>
          Domain
          <input name="domain" placeholder="example.test" />
        </label>
        <label>
          Tier
          <select name="tier" defaultValue="">
            {tiers.map((tier) => (
              <option key={tier || "empty"} value={tier}>
                {tier || "Unassigned"}
              </option>
            ))}
          </select>
        </label>
        <label>
          Country
          <input name="country" />
        </label>
        <label>
          Region
          <input name="region" placeholder="USA, EU, LATAM" />
        </label>
        <label>
          Careers URL
          <input name="careers_url" type="url" />
        </label>
        <label>
          ATS type
          <input name="ats_type" placeholder="greenhouse, lever, custom" />
        </label>
        <label>
          Visa
          <select name="visa_friendly_intern" defaultValue="unknown">
            {visaValues.map((visa) => (
              <option key={visa} value={visa}>
                {visa}
              </option>
            ))}
          </select>
        </label>
        <label>
          Status
          <select name="status" defaultValue="active">
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </label>
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Creating..." : "Create company"}
      </button>
    </form>
  );
}

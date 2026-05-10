"use client";

import { FormEvent, useMemo, useState } from "react";
import {
  createApplication,
  type ApplicationPayload,
  type Company,
  type Contact,
  type User
} from "../../lib/api";

const types = ["formal", "speculative", "referral", "networking", "other"] as const;
const statuses = ["researching", "contacted", "responded", "interviewing", "offer", "rejected", "paused"] as const;

function nullableValue(formData: FormData, name: string) {
  const raw = formData.get(name)?.toString().trim();
  return raw ? raw : null;
}

export function ApplicationForm({
  companies,
  users,
  contacts
}: {
  companies: Company[];
  users: User[];
  contacts: Contact[];
}) {
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedCompanyId, setSelectedCompanyId] = useState("");

  const availableContacts = useMemo(
    () =>
      selectedCompanyId
        ? contacts.filter((contact) => contact.company_id === selectedCompanyId)
        : contacts,
    [contacts, selectedCompanyId]
  );

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const formData = new FormData(event.currentTarget);
    const payload: ApplicationPayload = {
      company_id: nullableValue(formData, "company_id") ?? "",
      user_id: nullableValue(formData, "user_id") ?? "",
      contact_id: nullableValue(formData, "contact_id"),
      type: nullableValue(formData, "type") as ApplicationPayload["type"],
      status: nullableValue(formData, "status") as ApplicationPayload["status"],
      next_action: nullableValue(formData, "next_action"),
      next_action_due: nullableValue(formData, "next_action_due"),
      notes: nullableValue(formData, "notes")
    };

    try {
      await createApplication(payload);
      event.currentTarget.reset();
      setSelectedCompanyId("");
      window.location.reload();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Could not create application");
    } finally {
      setIsSubmitting(false);
    }
  }

  const isDisabled = companies.length === 0 || users.length === 0;

  return (
    <form className="panel form" onSubmit={onSubmit}>
      <h2>Add application</h2>
      {error ? <p className="notice error">{error}</p> : null}
      {isDisabled ? <p className="notice error">Create at least one company and one user first.</p> : null}

      <div className="form-grid">
        <label>
          Company
          <select
            name="company_id"
            required
            disabled={isDisabled}
            value={selectedCompanyId}
            onChange={(event) => setSelectedCompanyId(event.target.value)}
          >
            <option value="">Select company</option>
            {companies.map((company) => (
              <option key={company.id} value={company.id}>
                {company.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          User
          <select name="user_id" required disabled={isDisabled}>
            <option value="">Select user</option>
            {users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Contact
          <select name="contact_id" disabled={isDisabled}>
            <option value="">No contact</option>
            {availableContacts.map((contact) => (
              <option key={contact.id} value={contact.id}>
                {contact.full_name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Type
          <select name="type" defaultValue="formal" disabled={isDisabled}>
            {types.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </label>
        <label>
          Status
          <select name="status" defaultValue="researching" disabled={isDisabled}>
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </label>
        <label>
          Next action
          <input name="next_action" disabled={isDisabled} />
        </label>
        <label>
          Next action due
          <input name="next_action_due" type="date" disabled={isDisabled} />
        </label>
      </div>
      <label className="full-width">
        Notes
        <textarea name="notes" disabled={isDisabled} />
      </label>
      <button type="submit" disabled={isSubmitting || isDisabled}>
        {isSubmitting ? "Creating..." : "Create application"}
      </button>
    </form>
  );
}


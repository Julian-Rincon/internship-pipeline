"use client";

import { FormEvent, useState } from "react";
import {
  claimCompany,
  releaseCompany,
  updateCompanyOwnership,
  type Company,
  type User
} from "../../../lib/api";

const ownedStatuses: Company["ownership_status"][] = ["claimed", "paused", "done"];

function reload() {
  window.location.reload();
}

export function OwnershipPanel({ company, users }: { company: Company; users: User[] }) {
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onClaim(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const formData = new FormData(event.currentTarget);
    const userId = formData.get("user_id")?.toString();
    const notes = formData.get("ownership_notes")?.toString().trim();

    if (!userId) {
      setError("Select a user before claiming this company.");
      setIsSubmitting(false);
      return;
    }

    try {
      await claimCompany(company.id, {
        user_id: userId,
        ownership_notes: notes || null
      });
      reload();
    } catch (claimError) {
      setError(claimError instanceof Error ? claimError.message : "Could not claim company");
      setIsSubmitting(false);
    }
  }

  async function onRelease() {
    setError(null);
    setIsSubmitting(true);

    try {
      await releaseCompany(company.id);
      reload();
    } catch (releaseError) {
      setError(releaseError instanceof Error ? releaseError.message : "Could not release company");
      setIsSubmitting(false);
    }
  }

  async function onStatusChange(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const formData = new FormData(event.currentTarget);
    const ownershipStatus = formData.get("ownership_status")?.toString() as
      | "claimed"
      | "paused"
      | "done"
      | undefined;
    const notes = formData.get("ownership_notes")?.toString().trim();

    try {
      await updateCompanyOwnership(company.id, {
        ownership_status: ownershipStatus,
        ownership_notes: notes || null
      });
      reload();
    } catch (statusError) {
      setError(statusError instanceof Error ? statusError.message : "Could not update ownership");
      setIsSubmitting(false);
    }
  }

  return (
    <div className="panel" style={{ marginTop: 16 }}>
      <h2>Team coordination</h2>
      {error ? <p className="notice error">{error}</p> : null}

      {company.owner_user_id ? (
        <form className="form compact-form" onSubmit={onStatusChange}>
          <div className="form-grid">
            <label>
              Ownership status
              <select name="ownership_status" defaultValue={company.ownership_status}>
                {ownedStatuses.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Ownership notes
              <input name="ownership_notes" defaultValue={company.ownership_notes ?? ""} />
            </label>
          </div>
          <div className="button-row" style={{ marginTop: 16 }}>
            <button type="submit" disabled={isSubmitting}>
              Save ownership
            </button>
            <button className="danger-button" type="button" onClick={onRelease} disabled={isSubmitting}>
              Release
            </button>
          </div>
        </form>
      ) : (
        <form className="form compact-form" onSubmit={onClaim}>
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
              Ownership notes
              <input name="ownership_notes" placeholder="Optional coordination notes" />
            </label>
          </div>
          <button type="submit" disabled={isSubmitting || users.length === 0}>
            Claim company
          </button>
          {users.length === 0 ? <p className="muted">Create a user before claiming companies.</p> : null}
        </form>
      )}
    </div>
  );
}

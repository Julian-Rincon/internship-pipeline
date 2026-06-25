"use client";

import { FormEvent, useState } from "react";
import { createInterview, type InterviewPayload } from "../../lib/api";

const interviewTypes = ["phone", "technical", "system_design", "behavioral", "onsite", "hr"] as const;
const outcomes = ["pending", "passed", "failed"] as const;

function nullableValue(formData: FormData, name: string) {
  const raw = formData.get(name)?.toString().trim();
  return raw ? raw : null;
}

export function InterviewForm() {
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const formData = new FormData(event.currentTarget);
    const payload: InterviewPayload = {
      company_id: nullableValue(formData, "company_id") ?? "",
      user_id: nullableValue(formData, "user_id") ?? "",
      interview_type: nullableValue(formData, "interview_type") as InterviewPayload["interview_type"],
      scheduled_at: nullableValue(formData, "scheduled_at"),
      interviewer_role: nullableValue(formData, "interviewer_role"),
      outcome: (nullableValue(formData, "outcome") ?? "pending") as InterviewPayload["outcome"],
      notes: nullableValue(formData, "notes"),
    };

    try {
      await createInterview(payload);
      event.currentTarget.reset();
      window.location.reload();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Could not create interview");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="panel form" onSubmit={onSubmit}>
      <h2>Add interview</h2>
      {error ? <p className="notice error">{error}</p> : null}

      <div className="form-grid">
        <label>
          Company ID
          <input name="company_id" required placeholder="UUID" />
        </label>
        <label>
          User ID
          <input name="user_id" required placeholder="UUID" />
        </label>
        <label>
          Interview type
          <select name="interview_type" defaultValue="technical">
            {interviewTypes.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>
        <label>
          Outcome
          <select name="outcome" defaultValue="pending">
            {outcomes.map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>
        </label>
        <label>
          Scheduled at
          <input name="scheduled_at" type="datetime-local" />
        </label>
        <label>
          Interviewer role
          <input name="interviewer_role" placeholder="e.g. Senior Engineer" />
        </label>
      </div>
      <label className="full-width">
        Notes
        <textarea name="notes" />
      </label>
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Creating..." : "Create interview"}
      </button>
    </form>
  );
}

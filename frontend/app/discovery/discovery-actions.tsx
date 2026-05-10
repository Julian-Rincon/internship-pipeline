"use client";

import { useState } from "react";
import {
  approveDiscoveryCandidate,
  rejectDiscoveryCandidate,
  runDemoDiscovery,
  type DiscoveryCandidate
} from "../../lib/api";

function reload() {
  window.location.reload();
}

export function RunDemoDiscoveryButton() {
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  async function onRun() {
    setMessage(null);
    setError(null);
    setIsRunning(true);

    try {
      const result = await runDemoDiscovery();
      setMessage(
        `Created ${result.candidates_created} candidates and ${result.job_postings_created} job postings.`
      );
      reload();
    } catch (runError) {
      setError(runError instanceof Error ? runError.message : "Could not run demo discovery");
      setIsRunning(false);
    }
  }

  return (
    <div className="action-block">
      <button type="button" onClick={onRun} disabled={isRunning}>
        {isRunning ? "Running..." : "Run demo discovery"}
      </button>
      {message ? <p className="muted">{message}</p> : null}
      {error ? <p className="notice error">{error}</p> : null}
    </div>
  );
}

export function CandidateActions({ candidate }: { candidate: DiscoveryCandidate }) {
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const canReview = candidate.status === "pending_review" || candidate.status === "ignored";

  async function onApprove() {
    setError(null);
    setIsSubmitting(true);

    try {
      await approveDiscoveryCandidate(candidate.id);
      reload();
    } catch (approveError) {
      setError(approveError instanceof Error ? approveError.message : "Could not approve candidate");
      setIsSubmitting(false);
    }
  }

  async function onReject() {
    setError(null);
    setIsSubmitting(true);

    try {
      await rejectDiscoveryCandidate(candidate.id);
      reload();
    } catch (rejectError) {
      setError(rejectError instanceof Error ? rejectError.message : "Could not reject candidate");
      setIsSubmitting(false);
    }
  }

  return (
    <div>
      {canReview ? (
        <div className="button-row">
          <button type="button" onClick={onApprove} disabled={isSubmitting}>
            Approve
          </button>
          <button className="danger-button" type="button" onClick={onReject} disabled={isSubmitting}>
            Reject
          </button>
        </div>
      ) : (
        <span className="muted">Reviewed</span>
      )}
      {error ? <p className="notice error">{error}</p> : null}
    </div>
  );
}

import { CandidateActions, RunDemoDiscoveryButton } from "./discovery-actions";
import { getDiscoveryCandidates, type DiscoveryCandidate } from "../../lib/api";
import Link from "next/link";

export const dynamic = "force-dynamic";

const statuses: DiscoveryCandidate["status"][] = [
  "pending_review",
  "approved",
  "rejected",
  "ignored"
];

function CandidateLink({ href, label }: { href: string | null; label: string }) {
  if (!href) {
    return <>-</>;
  }

  return (
    <a href={href} target="_blank" rel="noreferrer">
      {label}
    </a>
  );
}

function CandidateTable({
  status,
  candidates
}: {
  status: DiscoveryCandidate["status"];
  candidates: DiscoveryCandidate[];
}) {
  const statusCandidates = candidates.filter((candidate) => candidate.status === status);

  return (
    <section className="panel discovery-section">
      <h2>{status.replace("_", " ")}</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Company</th>
              <th>Source</th>
              <th>Detected role</th>
              <th>Job URL</th>
              <th>Careers</th>
              <th>Confidence</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {statusCandidates.length === 0 ? (
              <tr>
                <td colSpan={8} className="muted">
                  No candidates in this status.
                </td>
              </tr>
            ) : (
              statusCandidates.map((candidate) => (
                <tr key={candidate.id}>
                  <td>
                    <strong>{candidate.company_name}</strong>
                    <br />
                    <span className="muted">{candidate.domain ?? "-"}</span>
                  </td>
                  <td>{candidate.source}</td>
                  <td>{candidate.detected_job_title ?? "-"}</td>
                  <td>
                    {candidate.detected_job_url ? (
                      <>
                        <CandidateLink href={candidate.detected_job_url} label="Job" />
                        <br />
                        <Link href="/job-postings">Job postings</Link>
                      </>
                    ) : (
                      "-"
                    )}
                  </td>
                  <td>
                    <CandidateLink href={candidate.careers_url} label="Careers" />
                  </td>
                  <td>
                    {candidate.confidence_score === null
                      ? "-"
                      : `${Math.round(candidate.confidence_score * 100)}%`}
                  </td>
                  <td>
                    <span className={`badge badge-${candidate.status}`}>{candidate.status}</span>
                  </td>
                  <td>
                    <CandidateActions candidate={candidate} />
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default async function DiscoveryPage() {
  const result = await getDiscoveryCandidates();
  const candidates = result.data;

  return (
    <section>
      <h1>Discovery</h1>
      <p className="muted">
        Demo-only discovery creates fictional candidates for human review before anything enters the
        official companies list.
      </p>

      <RunDemoDiscoveryButton />
      <div className="breadcrumb-row" style={{ marginTop: 16 }}>
        <Link href="/discovery/sources">Manage ATS sources</Link>
      </div>

      {!result.ok ? <p className="notice error">Could not load discovery candidates: {result.error}</p> : null}

      <div className="discovery-stack">
        {statuses.map((status) => (
          <CandidateTable candidates={candidates} status={status} key={status} />
        ))}
      </div>
    </section>
  );
}

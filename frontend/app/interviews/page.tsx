import { getInterviews } from "../../lib/api";
import { InterviewForm } from "./interview-form";

export const dynamic = "force-dynamic";

const outcomeBadge: Record<string, string> = {
  passed: "badge badge-green",
  failed: "badge badge-red",
  pending: "badge badge-yellow",
};

export default async function InterviewsPage() {
  const interviewsResult = await getInterviews();
  const interviews = interviewsResult.data;

  return (
    <section>
      <h1>Interview Knowledge Base</h1>
      <p className="muted">
        Track interview rounds, questions asked, and outcomes for each company.
      </p>

      <InterviewForm />

      {!interviewsResult.ok ? (
        <p className="notice error">Could not load interviews: {interviewsResult.error}</p>
      ) : null}

      <div className="panel" style={{ marginTop: "20px" }}>
        <h2>All interviews</h2>
        {interviews.length === 0 ? (
          <p className="muted">No interviews recorded yet.</p>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Company</th>
                  <th>User</th>
                  <th>Type</th>
                  <th>Outcome</th>
                  <th>Scheduled</th>
                  <th>Interviewer role</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                {interviews.map((interview) => (
                  <tr key={interview.id}>
                    <td>
                      <span className="muted" style={{ fontFamily: "monospace", fontSize: "11px" }}>
                        {interview.company_id.slice(0, 8)}…
                      </span>
                    </td>
                    <td>
                      <span className="muted" style={{ fontFamily: "monospace", fontSize: "11px" }}>
                        {interview.user_id.slice(0, 8)}…
                      </span>
                    </td>
                    <td>
                      <span className="badge">{interview.interview_type}</span>
                    </td>
                    <td>
                      <span className={outcomeBadge[interview.outcome] ?? "badge"}>
                        {interview.outcome}
                      </span>
                    </td>
                    <td className="muted">
                      {interview.scheduled_at
                        ? new Date(interview.scheduled_at).toLocaleDateString()
                        : "—"}
                    </td>
                    <td className="muted">{interview.interviewer_role ?? "—"}</td>
                    <td className="muted">{interview.notes ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}

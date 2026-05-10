import Link from "next/link";
import { getDashboardSummary } from "../lib/api";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const summaryResult = await getDashboardSummary();
  const summary = summaryResult.data;

  return (
    <section>
      <h1>Dashboard</h1>
      <p className="muted">
        Base operativa para registrar empresas target y validar el pipeline manualmente.
      </p>

      <div className="grid">
        <div className="panel metric">
          <div className="muted">Companies</div>
          <div className="metric-value">{summary.total_companies}</div>
        </div>
        <div className="panel metric">
          <div className="muted">Users</div>
          <div className="metric-value">{summary.total_users}</div>
        </div>
        <div className="panel metric">
          <div className="muted">Contacts</div>
          <div className="metric-value">{summary.total_contacts}</div>
        </div>
        <div className="panel metric">
          <div className="muted">Applications</div>
          <div className="metric-value">{summary.total_applications}</div>
        </div>
      </div>

      <div className="panel" style={{ marginTop: 16 }}>
        <h2>Reminders</h2>
        <div className="status-list">
          <span className="badge badge-high">overdue: {summary.overdue_reminders}</span>
          <span className="badge badge-medium">due today: {summary.due_today_reminders}</span>
          <span className="badge badge-low">due soon: {summary.due_soon_reminders}</span>
          <span className="badge badge-pending_review">
            pending review: {summary.pending_review_reminders}
          </span>
        </div>
        <p className="muted">
          Internal visibility for manual actions only. No emails or outreach are sent.
        </p>
        <Link href="/reminders">View reminders</Link>
      </div>

      <div className="panel" style={{ marginTop: 16 }}>
        <h2>Company ownership</h2>
        {!summaryResult.ok ? (
          <p className="notice error">Could not load summary: {summaryResult.error}</p>
        ) : null}
        <div className="status-list">
          <span className="badge badge-unclaimed">unclaimed: {summary.unclaimed_companies}</span>
          <span className="badge badge-claimed">claimed: {summary.claimed_companies}</span>
          <span className="badge badge-paused">paused: {summary.paused_companies}</span>
          <span className="badge badge-done">done: {summary.done_companies}</span>
        </div>
        <p className="muted">
          Manual ownership helps the team avoid duplicate effort before adding authentication or automation.
        </p>
        <Link href="/companies">View companies</Link>
      </div>

      <div className="panel" style={{ marginTop: 16 }}>
        <h2>Pipeline status</h2>
        {!summaryResult.ok ? (
          <p className="notice error">Could not load summary: {summaryResult.error}</p>
        ) : null}
        {summary.total_applications === 0 ? (
          <p className="muted">No applications yet.</p>
        ) : (
          <div className="status-list">
            {Object.entries(summary.applications_by_status).map(([status, count]) => (
              <span className="badge badge-in_progress" key={status}>
                {status}: {count}
              </span>
            ))}
          </div>
        )}
        <p className="muted">
          Track applications manually before adding automation, matching, scraping or outreach.
        </p>
        <Link href="/applications">View applications</Link>
      </div>
    </section>
  );
}

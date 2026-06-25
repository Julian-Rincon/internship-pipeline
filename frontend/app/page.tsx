import Link from "next/link";
import { getDashboardSummary } from "../lib/api";

export const dynamic = "force-dynamic";

const STATUS_COLORS: Record<string, string> = {
  researching: "badge-researching",
  contacted: "badge-contacted",
  responded: "badge-responded",
  interviewing: "badge-interviewing",
  offer: "badge-offer",
  rejected: "badge-rejected-app",
  paused: "badge-paused-app",
};

export default async function DashboardPage() {
  const summaryResult = await getDashboardSummary();
  const summary = summaryResult.data;

  return (
    <section>
      <h1 style={{ marginTop: 0, fontSize: 22, fontWeight: 800 }}>Dashboard</h1>
      <p className="muted" style={{ marginTop: 0, marginBottom: 20 }}>
        Pipeline operativo — empresas target, aplicaciones activas, candidatos por revisar.
      </p>

      {!summaryResult.ok && (
        <p className="notice error" style={{ marginBottom: 16 }}>
          Could not load summary: {summaryResult.error}
        </p>
      )}

      {/* Key metrics */}
      <div className="grid">
        <div className="panel metric">
          <div className="metric-label">Companies</div>
          <div className="metric-value">{summary.total_companies}</div>
          <div className="metric-sublabel">
            {summary.unclaimed_companies} unclaimed · {summary.claimed_companies} claimed
          </div>
        </div>
        <div className="panel metric">
          <div className="metric-label">Team Members</div>
          <div className="metric-value">{summary.total_users}</div>
          <div className="metric-sublabel">registered profiles</div>
        </div>
        <div className="panel metric">
          <div className="metric-label">Contacts</div>
          <div className="metric-value">{summary.total_contacts}</div>
          <div className="metric-sublabel">manual contacts</div>
        </div>
        <div className="panel metric">
          <div className="metric-label">Applications</div>
          <div className="metric-value">{summary.total_applications}</div>
          <div className="metric-sublabel">
            {summary.applications_by_status?.interviewing ?? 0} interviewing
          </div>
        </div>
      </div>

      {/* Reminders */}
      <div className="panel" style={{ marginTop: 14 }}>
        <h2>Reminders</h2>
        <div className="status-list">
          <span className="badge badge-high">
            🔴 overdue: {summary.overdue_reminders}
          </span>
          <span className="badge badge-medium">
            🟡 due today: {summary.due_today_reminders}
          </span>
          <span className="badge badge-low">
            🔵 due soon: {summary.due_soon_reminders}
          </span>
          <span className="badge badge-pending_review">
            ⏳ pending review: {summary.pending_review_reminders}
          </span>
        </div>
        <p className="muted">Internal visibility only — no emails or outreach sent.</p>
        <Link href="/reminders">View all reminders →</Link>
      </div>

      {/* Company ownership */}
      <div className="panel" style={{ marginTop: 14 }}>
        <h2>Company ownership</h2>
        <div className="status-list">
          <span className="badge badge-unclaimed">unclaimed: {summary.unclaimed_companies}</span>
          <span className="badge badge-claimed">claimed: {summary.claimed_companies}</span>
          <span className="badge badge-paused">paused: {summary.paused_companies}</span>
          <span className="badge badge-done">done: {summary.done_companies}</span>
        </div>
        <p className="muted">Claim companies to avoid duplicate research within the team.</p>
        <Link href="/companies">View companies →</Link>
      </div>

      {/* Pipeline status */}
      <div className="panel" style={{ marginTop: 14 }}>
        <h2>Pipeline status</h2>
        {summary.total_applications === 0 ? (
          <p className="muted">No applications yet. Start by adding a company and claiming it.</p>
        ) : (
          <div className="status-list">
            {Object.entries(summary.applications_by_status).map(([status, count]) => (
              <span className={`badge ${STATUS_COLORS[status] ?? "badge-in_progress"}`} key={status}>
                {status}: {String(count)}
              </span>
            ))}
          </div>
        )}
        <p className="muted">Update status and next action on each application manually.</p>
        <Link href="/applications">View applications →</Link>
      </div>

      {/* Quick actions */}
      <div className="panel" style={{ marginTop: 14 }}>
        <h2>Quick actions</h2>
        <div className="quick-actions">
          <Link href="/users" className="quick-action-link">
            👤 Add team member
          </Link>
          <Link href="/companies" className="quick-action-link">
            🏢 Add company
          </Link>
          <Link href="/discovery/sources" className="quick-action-link">
            🔍 Run discovery
          </Link>
          <Link href="/discovery" className="quick-action-link">
            ✅ Review candidates
          </Link>
          <Link href="/applications" className="quick-action-link">
            📋 New application
          </Link>
          <Link href="/job-postings" className="quick-action-link">
            📄 Job postings
          </Link>
        </div>
      </div>
    </section>
  );
}

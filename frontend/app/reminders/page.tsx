import { RemindersList } from "./reminders-list";
import { getReminders } from "../../lib/api";

export const dynamic = "force-dynamic";

export default async function RemindersPage() {
  const result = await getReminders();
  const reminders = result.data;

  return (
    <section>
      <h1>Reminders</h1>
      <p className="muted">
        Internal visibility for overdue and upcoming manual work. No emails, outreach, scraping or
        external automation run from this page.
      </p>

      <div className="grid">
        <div className="panel metric">
          <div className="muted">Total reminders</div>
          <div className="metric-value">{reminders.length}</div>
        </div>
      </div>

      {!result.ok ? <p className="notice error">Could not load reminders: {result.error}</p> : null}

      <RemindersList reminders={reminders} />

      <div className="panel" style={{ marginTop: 16 }}>
        <h2>n8n integration</h2>
        <p className="muted">
          n8n can query backend reminders for internal notification workflows. The included demo
          workflow formats a local summary only; it does not send email, outreach or external webhooks.
        </p>
        <p>
          Workflow export: <code>n8n/workflows/internal-reminders-demo.json</code>
        </p>
      </div>
    </section>
  );
}

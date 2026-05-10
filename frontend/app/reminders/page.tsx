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
    </section>
  );
}

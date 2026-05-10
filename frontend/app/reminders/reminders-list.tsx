"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { Reminder } from "../../lib/api";

const severities: Reminder["severity"][] = ["high", "medium", "low"];
const reminderTypes: Reminder["type"][] = [
  "application_overdue",
  "application_due_today",
  "application_due_soon",
  "discovery_pending_review",
  "claimed_company_stale"
];

function relatedHref(reminder: Reminder): string {
  if (reminder.related_entity_type === "application") {
    return "/applications";
  }
  if (reminder.related_entity_type === "discovery_candidate") {
    return "/discovery";
  }
  return `/companies/${reminder.related_entity_id}`;
}

export function RemindersList({ reminders }: { reminders: Reminder[] }) {
  const [severityFilter, setSeverityFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");

  const filteredReminders = useMemo(
    () =>
      reminders.filter(
        (reminder) =>
          (!severityFilter || reminder.severity === severityFilter) &&
          (!typeFilter || reminder.type === typeFilter)
      ),
    [reminders, severityFilter, typeFilter]
  );

  const severityCounts = useMemo(
    () =>
      severities.map((severity) => ({
        severity,
        count: reminders.filter((reminder) => reminder.severity === severity).length
      })),
    [reminders]
  );

  return (
    <div className="panel" style={{ marginTop: 16 }}>
      <div className="status-list">
        {severityCounts.map(({ severity, count }) => (
          <span className={`badge badge-${severity}`} key={severity}>
            {severity}: {count}
          </span>
        ))}
      </div>

      <div className="toolbar">
        <label>
          Severity
          <select value={severityFilter} onChange={(event) => setSeverityFilter(event.target.value)}>
            <option value="">All</option>
            {severities.map((severity) => (
              <option key={severity} value={severity}>
                {severity}
              </option>
            ))}
          </select>
        </label>
        <label>
          Type
          <select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)}>
            <option value="">All</option>
            {reminderTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Reminder</th>
              <th>Severity</th>
              <th>Type</th>
              <th>Due</th>
              <th>Related</th>
            </tr>
          </thead>
          <tbody>
            {filteredReminders.length === 0 ? (
              <tr>
                <td colSpan={5} className="muted">
                  No reminders match the current filters.
                </td>
              </tr>
            ) : (
              filteredReminders.map((reminder) => (
                <tr key={reminder.id}>
                  <td>
                    <strong>{reminder.title}</strong>
                    <br />
                    <span className="muted">{reminder.description}</span>
                  </td>
                  <td>
                    <span className={`badge badge-${reminder.severity}`}>{reminder.severity}</span>
                  </td>
                  <td>{reminder.type}</td>
                  <td>{reminder.due_date ?? "-"}</td>
                  <td>
                    <Link href={relatedHref(reminder)}>{reminder.related_entity_type}</Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

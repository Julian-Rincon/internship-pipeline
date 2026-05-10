"use client";

import Link from "next/link";
import { FormEvent, useMemo, useState } from "react";
import {
  deleteApplication,
  updateApplication,
  type Application,
  type ApplicationPayload,
  type Company,
  type Contact,
  type User
} from "../../lib/api";

const statuses: Application["status"][] = [
  "researching",
  "contacted",
  "responded",
  "interviewing",
  "offer",
  "rejected",
  "paused"
];
const types: Application["type"][] = ["formal", "speculative", "referral", "networking", "other"];

type ViewMode = "list" | "board";

function nullableValue(formData: FormData, name: string) {
  const raw = formData.get(name)?.toString().trim();
  return raw ? raw : null;
}

function ApplicationEditForm({ application }: { application: Application }) {
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const formData = new FormData(event.currentTarget);
    const payload: Partial<ApplicationPayload> = {
      status: nullableValue(formData, "status") as ApplicationPayload["status"],
      next_action: nullableValue(formData, "next_action"),
      next_action_due: nullableValue(formData, "next_action_due"),
      notes: nullableValue(formData, "notes")
    };

    try {
      await updateApplication(application.id, payload);
      window.location.reload();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Could not update application");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <details className="edit-details">
      <summary>Edit</summary>
      <form className="form compact-form" onSubmit={onSubmit}>
        {error ? <p className="notice error">{error}</p> : null}
        <div className="form-grid">
          <label>
            Status
            <select name="status" defaultValue={application.status}>
              {statuses.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </label>
          <label>
            Next action
            <input name="next_action" defaultValue={application.next_action ?? ""} />
          </label>
          <label>
            Next action due
            <input name="next_action_due" type="date" defaultValue={application.next_action_due ?? ""} />
          </label>
        </div>
        <label className="full-width">
          Notes
          <textarea name="notes" defaultValue={application.notes ?? ""} />
        </label>
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : "Save"}
        </button>
      </form>
    </details>
  );
}

function DeleteButton({ applicationId }: { applicationId: string }) {
  const [error, setError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  async function onDelete() {
    if (!window.confirm("Delete this application?")) {
      return;
    }

    setError(null);
    setIsDeleting(true);
    try {
      await deleteApplication(applicationId);
      window.location.reload();
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Could not delete application");
      setIsDeleting(false);
    }
  }

  return (
    <div>
      <button className="danger-button" type="button" onClick={onDelete} disabled={isDeleting}>
        {isDeleting ? "Deleting..." : "Delete"}
      </button>
      {error ? <p className="notice error">{error}</p> : null}
    </div>
  );
}

function ApplicationCard({
  application,
  company,
  user,
  contactName
}: {
  application: Application;
  company: Company | undefined;
  user: User | undefined;
  contactName: string;
}) {
  return (
    <div className="kanban-card">
      <strong>
        {company ? <Link href={`/companies/${company.id}`}>{company.name}</Link> : "Unknown company"}
      </strong>
      <span className="muted">
        {user ? <Link href={`/users/${user.id}`}>{user.name}</Link> : "Unknown user"}
      </span>
      <span className="muted">{contactName}</span>
      <div className="status-list">
        <span className="badge badge-in_progress">{application.type}</span>
        <span className="badge badge-ready">{application.status}</span>
      </div>
      <p>{application.next_action ?? "No next action"}</p>
      <span className="muted">Due: {application.next_action_due ?? "-"}</span>
      <ApplicationEditForm application={application} />
      <DeleteButton applicationId={application.id} />
    </div>
  );
}

export function ApplicationsTracker({
  applications,
  companies,
  users,
  contacts
}: {
  applications: Application[];
  companies: Company[];
  users: User[];
  contacts: Contact[];
}) {
  const [viewMode, setViewMode] = useState<ViewMode>("list");
  const [statusFilter, setStatusFilter] = useState("");
  const [userFilter, setUserFilter] = useState("");
  const [companyFilter, setCompanyFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");

  const companyById = useMemo(() => new Map(companies.map((company) => [company.id, company])), [companies]);
  const userById = useMemo(() => new Map(users.map((user) => [user.id, user])), [users]);
  const contactById = useMemo(() => new Map(contacts.map((contact) => [contact.id, contact.full_name])), [contacts]);

  const filteredApplications = applications.filter((application) => {
    return (
      (!statusFilter || application.status === statusFilter) &&
      (!userFilter || application.user_id === userFilter) &&
      (!companyFilter || application.company_id === companyFilter) &&
      (!typeFilter || application.type === typeFilter)
    );
  });

  return (
    <div className="panel" style={{ marginTop: 16 }}>
      <div className="toolbar">
        <label>
          View
          <select value={viewMode} onChange={(event) => setViewMode(event.target.value as ViewMode)}>
            <option value="list">List</option>
            <option value="board">Board</option>
          </select>
        </label>
        <label>
          Status
          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            <option value="">All</option>
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </label>
        <label>
          User
          <select value={userFilter} onChange={(event) => setUserFilter(event.target.value)}>
            <option value="">All</option>
            {users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Company
          <select value={companyFilter} onChange={(event) => setCompanyFilter(event.target.value)}>
            <option value="">All</option>
            {companies.map((company) => (
              <option key={company.id} value={company.id}>
                {company.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Type
          <select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)}>
            <option value="">All</option>
            {types.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </label>
      </div>

      {viewMode === "list" ? (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Company</th>
                <th>User</th>
                <th>Contact</th>
                <th>Type</th>
                <th>Status</th>
                <th>Next action</th>
                <th>Due</th>
                <th>Edit</th>
                <th>Delete</th>
              </tr>
            </thead>
            <tbody>
              {filteredApplications.length === 0 ? (
                <tr>
                  <td colSpan={9} className="muted">
                    No applications match the filters.
                  </td>
                </tr>
              ) : (
                filteredApplications.map((application) => (
                  <tr key={application.id}>
                    <td>
                      {companyById.get(application.company_id) ? (
                        <Link href={`/companies/${application.company_id}`}>
                          {companyById.get(application.company_id)?.name}
                        </Link>
                      ) : (
                        "Unknown company"
                      )}
                    </td>
                    <td>
                      {userById.get(application.user_id) ? (
                        <Link href={`/users/${application.user_id}`}>
                          {userById.get(application.user_id)?.name}
                        </Link>
                      ) : (
                        "Unknown user"
                      )}
                    </td>
                    <td>
                      {application.contact_id
                        ? contactById.get(application.contact_id) ?? "Unknown contact"
                        : "-"}
                    </td>
                    <td>{application.type}</td>
                    <td>{application.status}</td>
                    <td>{application.next_action ?? "-"}</td>
                    <td>{application.next_action_due ?? "-"}</td>
                    <td>
                      <ApplicationEditForm application={application} />
                    </td>
                    <td>
                      <DeleteButton applicationId={application.id} />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="kanban-board">
          {statuses.map((status) => {
            const statusApplications = filteredApplications.filter(
              (application) => application.status === status
            );
            return (
              <section className="kanban-column" key={status}>
                <h3>{status}</h3>
                {statusApplications.length === 0 ? (
                  <p className="muted">No applications</p>
                ) : (
                  statusApplications.map((application) => (
                    <ApplicationCard
                      application={application}
                      company={companyById.get(application.company_id)}
                      user={userById.get(application.user_id)}
                      contactName={
                        application.contact_id
                          ? contactById.get(application.contact_id) ?? "Unknown contact"
                          : "No contact"
                      }
                      key={application.id}
                    />
                  ))
                )}
              </section>
            );
          })}
        </div>
      )}
    </div>
  );
}

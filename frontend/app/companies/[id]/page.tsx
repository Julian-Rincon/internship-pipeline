import Link from "next/link";
import { OwnershipPanel } from "./ownership-panel";
import {
  getCompany,
  getCompanyApplications,
  getCompanyContacts,
  getUsers
} from "../../../lib/api";

export const dynamic = "force-dynamic";

function value(value: string | boolean | null | undefined) {
  if (typeof value === "boolean") {
    return value ? "yes" : "no";
  }

  return value ?? "-";
}

export default async function CompanyDetailPage({ params }: { params: { id: string } }) {
  const [companyResult, contactsResult, applicationsResult, usersResult] = await Promise.all([
    getCompany(params.id),
    getCompanyContacts(params.id),
    getCompanyApplications(params.id),
    getUsers()
  ]);

  const company = companyResult.data;
  const contacts = contactsResult.data;
  const applications = applicationsResult.data;
  const userById = new Map(usersResult.data.map((user) => [user.id, user]));
  const owner = company?.owner_user_id ? userById.get(company.owner_user_id) : null;
  const contactById = new Map(contacts.map((contact) => [contact.id, contact]));

  if (!company) {
    const errorMessage = companyResult.ok ? "Company not found." : companyResult.error;
    return (
      <section>
        <p className="notice error">Could not load company: {errorMessage}</p>
        <Link href="/companies">Back to companies</Link>
      </section>
    );
  }

  return (
    <section>
      <div className="breadcrumb-row">
        <Link href="/companies">Companies</Link>
        <Link href="/contacts">Contacts</Link>
        <Link href="/applications">Applications</Link>
      </div>

      <h1>{company.name}</h1>
      <p className="muted">Manual company detail. No automated enrichment runs in this phase.</p>

      <div className="panel detail-grid">
        <div>
          <span className="muted">Domain</span>
          <strong>{value(company.domain)}</strong>
        </div>
        <div>
          <span className="muted">Tier</span>
          <strong>{value(company.tier)}</strong>
        </div>
        <div>
          <span className="muted">Country</span>
          <strong>{value(company.country)}</strong>
        </div>
        <div>
          <span className="muted">Region</span>
          <strong>{value(company.region)}</strong>
        </div>
        <div>
          <span className="muted">Careers URL</span>
          {company.careers_url ? (
            <a href={company.careers_url} target="_blank" rel="noreferrer">
              {company.careers_url}
            </a>
          ) : (
            <strong>-</strong>
          )}
        </div>
        <div>
          <span className="muted">ATS type</span>
          <strong>{value(company.ats_type)}</strong>
        </div>
        <div>
          <span className="muted">Visa friendly intern</span>
          <strong>{value(company.visa_friendly_intern)}</strong>
        </div>
        <div>
          <span className="muted">Status</span>
          <strong>{company.status}</strong>
        </div>
        <div>
          <span className="muted">Owner</span>
          <strong>{owner?.name ?? "-"}</strong>
        </div>
        <div>
          <span className="muted">Ownership status</span>
          <strong>{company.ownership_status}</strong>
        </div>
        <div>
          <span className="muted">Claimed at</span>
          <strong>{value(company.claimed_at)}</strong>
        </div>
        <div className="wide-detail">
          <span className="muted">Ownership notes</span>
          <strong>{value(company.ownership_notes)}</strong>
        </div>
      </div>

      <OwnershipPanel company={company} users={usersResult.data} />

      <div className="panel table-wrap" style={{ marginTop: 16 }}>
        <h2>Related contacts</h2>
        {!contactsResult.ok ? (
          <p className="notice error">Could not load contacts: {contactsResult.error}</p>
        ) : null}
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Role</th>
              <th>Email</th>
              <th>Source</th>
              <th>Contacted</th>
            </tr>
          </thead>
          <tbody>
            {contacts.length === 0 ? (
              <tr>
                <td colSpan={5} className="muted">
                  No contacts linked to this company.
                </td>
              </tr>
            ) : (
              contacts.map((contact) => (
                <tr key={contact.id}>
                  <td>
                    <strong>{contact.full_name}</strong>
                  </td>
                  <td>{value(contact.role)}</td>
                  <td>{value(contact.email)}</td>
                  <td>{contact.source}</td>
                  <td>{contact.contacted ? "yes" : "no"}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="panel table-wrap" style={{ marginTop: 16 }}>
        <h2>Related applications</h2>
        {!applicationsResult.ok ? (
          <p className="notice error">Could not load applications: {applicationsResult.error}</p>
        ) : null}
        <table>
          <thead>
            <tr>
              <th>User</th>
              <th>Contact</th>
              <th>Type</th>
              <th>Status</th>
              <th>Next action</th>
              <th>Due</th>
            </tr>
          </thead>
          <tbody>
            {applications.length === 0 ? (
              <tr>
                <td colSpan={6} className="muted">
                  No applications linked to this company.
                </td>
              </tr>
            ) : (
              applications.map((application) => {
                const user = userById.get(application.user_id);
                const contact = application.contact_id ? contactById.get(application.contact_id) : null;
                return (
                  <tr key={application.id}>
                    <td>
                      {user ? <Link href={`/users/${user.id}`}>{user.name}</Link> : "Unknown user"}
                    </td>
                    <td>{contact?.full_name ?? "-"}</td>
                    <td>{application.type}</td>
                    <td>{application.status}</td>
                    <td>{value(application.next_action)}</td>
                    <td>{value(application.next_action_due)}</td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

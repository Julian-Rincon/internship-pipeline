import Link from "next/link";
import {
  getCompanies,
  getContacts,
  getUser,
  getUserApplications
} from "../../../lib/api";
import { ProfileStatusBadge } from "../user-forms";

export const dynamic = "force-dynamic";

function value(value: string | null | undefined) {
  return value ?? "-";
}

function listValue(values: string[] | null) {
  return values && values.length > 0 ? values.join(", ") : "-";
}

export default async function UserDetailPage({ params }: { params: { id: string } }) {
  const [userResult, applicationsResult, companiesResult, contactsResult] = await Promise.all([
    getUser(params.id),
    getUserApplications(params.id),
    getCompanies(),
    getContacts()
  ]);

  const user = userResult.data;
  const applications = applicationsResult.data;
  const companyById = new Map(companiesResult.data.map((company) => [company.id, company]));
  const contactById = new Map(contactsResult.data.map((contact) => [contact.id, contact]));

  if (!user) {
    const errorMessage = userResult.ok ? "User not found." : userResult.error;
    return (
      <section>
        <p className="notice error">Could not load user: {errorMessage}</p>
        <Link href="/users">Back to users</Link>
      </section>
    );
  }

  return (
    <section>
      <div className="breadcrumb-row">
        <Link href="/users">Users</Link>
        <Link href="/applications">Applications</Link>
      </div>

      <h1>{user.name}</h1>
      <p className="muted">Progressive user profile. Matching is not implemented in this phase.</p>

      <div className="panel detail-grid">
        <div>
          <span className="muted">Email</span>
          <strong>{user.email}</strong>
        </div>
        <div>
          <span className="muted">Role</span>
          <strong>{user.role}</strong>
        </div>
        <div>
          <span className="muted">Profile status</span>
          <ProfileStatusBadge status={user.profile_status} />
        </div>
        <div>
          <span className="muted">GitHub</span>
          <strong>{value(user.github_handle)}</strong>
        </div>
        <div>
          <span className="muted">LinkedIn</span>
          {user.linkedin_url ? (
            <a href={user.linkedin_url} target="_blank" rel="noreferrer">
              {user.linkedin_url}
            </a>
          ) : (
            <strong>-</strong>
          )}
        </div>
        <div>
          <span className="muted">Portfolio</span>
          {user.portfolio_url ? (
            <a href={user.portfolio_url} target="_blank" rel="noreferrer">
              {user.portfolio_url}
            </a>
          ) : (
            <strong>-</strong>
          )}
        </div>
        <div>
          <span className="muted">CV</span>
          {user.cv_url ? (
            <a href={user.cv_url} target="_blank" rel="noreferrer">
              {user.cv_url}
            </a>
          ) : (
            <strong>-</strong>
          )}
        </div>
        <div>
          <span className="muted">Target roles</span>
          <strong>{listValue(user.target_roles)}</strong>
        </div>
        <div>
          <span className="muted">Target regions</span>
          <strong>{listValue(user.target_regions)}</strong>
        </div>
        <div>
          <span className="muted">Target countries</span>
          <strong>{listValue(user.target_countries)}</strong>
        </div>
        <div>
          <span className="muted">Target company types</span>
          <strong>{listValue(user.target_company_types)}</strong>
        </div>
        <div>
          <span className="muted">Preferred industries</span>
          <strong>{listValue(user.preferred_industries)}</strong>
        </div>
        <div>
          <span className="muted">Technical interests</span>
          <strong>{listValue(user.technical_interests)}</strong>
        </div>
        <div>
          <span className="muted">Strong skills</span>
          <strong>{listValue(user.strong_skills)}</strong>
        </div>
        <div>
          <span className="muted">Learning goals</span>
          <strong>{listValue(user.learning_goals)}</strong>
        </div>
        <div className="wide-detail">
          <span className="muted">Internship goals</span>
          <strong>{value(user.internship_goals)}</strong>
        </div>
      </div>

      <div className="panel table-wrap" style={{ marginTop: 16 }}>
        <h2>Assigned applications</h2>
        {!applicationsResult.ok ? (
          <p className="notice error">Could not load applications: {applicationsResult.error}</p>
        ) : null}
        <table>
          <thead>
            <tr>
              <th>Company</th>
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
                  No applications assigned to this user.
                </td>
              </tr>
            ) : (
              applications.map((application) => {
                const company = companyById.get(application.company_id);
                const contact = application.contact_id ? contactById.get(application.contact_id) : null;
                return (
                  <tr key={application.id}>
                    <td>
                      {company ? (
                        <Link href={`/companies/${company.id}`}>{company.name}</Link>
                      ) : (
                        "Unknown company"
                      )}
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

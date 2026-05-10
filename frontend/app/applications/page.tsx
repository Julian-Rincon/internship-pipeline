import { getApplications, getCompanies, getContacts, getUsers } from "../../lib/api";
import { ApplicationForm } from "./application-form";
import { ApplicationsTracker } from "./applications-tracker";

export const dynamic = "force-dynamic";

export default async function ApplicationsPage() {
  const [applicationsResult, companiesResult, usersResult, contactsResult] = await Promise.all([
    getApplications(),
    getCompanies(),
    getUsers(),
    getContacts()
  ]);

  const applications = applicationsResult.data;
  const companies = companiesResult.data;
  const users = usersResult.data;
  const contacts = contactsResult.data;

  return (
    <section>
      <h1>Applications</h1>
      <p className="muted">
        Manual pipeline tracker. No outreach, matching or automation runs in this phase.
      </p>

      <ApplicationForm companies={companies} users={users} contacts={contacts} />

      {!applicationsResult.ok ? (
        <p className="notice error">Could not load applications: {applicationsResult.error}</p>
      ) : null}
      <ApplicationsTracker
        applications={applications}
        companies={companies}
        users={users}
        contacts={contacts}
      />
    </section>
  );
}

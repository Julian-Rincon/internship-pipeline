import { getCompanies, getContacts } from "../../lib/api";
import { ContactForm } from "./contact-form";

export const dynamic = "force-dynamic";

export default async function ContactsPage() {
  const [contactsResult, companiesResult] = await Promise.all([getContacts(), getCompanies()]);
  const contacts = contactsResult.data;
  const companies = companiesResult.data;
  const companyById = new Map(companies.map((company) => [company.id, company.name]));

  return (
    <section>
      <h1>Contacts</h1>
      <p className="muted">
        Manual, fictional contacts only. No enrichment, scraping or outreach runs in this phase.
      </p>

      <ContactForm companies={companies} />

      <div className="panel table-wrap" style={{ marginTop: 16 }}>
        {!contactsResult.ok ? (
          <p className="notice error">Could not load contacts: {contactsResult.error}</p>
        ) : null}
        {!companiesResult.ok ? (
          <p className="notice error">Could not load companies: {companiesResult.error}</p>
        ) : null}
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Role</th>
              <th>Company</th>
              <th>Source</th>
              <th>Affinity</th>
              <th>Contacted</th>
            </tr>
          </thead>
          <tbody>
            {contacts.length === 0 ? (
              <tr>
                <td colSpan={6} className="muted">
                  No contacts yet.
                </td>
              </tr>
            ) : (
              contacts.map((contact) => (
                <tr key={contact.id}>
                  <td>
                    <strong>{contact.full_name}</strong>
                    <br />
                    <span className="muted">{contact.email ?? "No email"}</span>
                  </td>
                  <td>{contact.role ?? "-"}</td>
                  <td>{companyById.get(contact.company_id) ?? "Unknown company"}</td>
                  <td>{contact.source}</td>
                  <td>{contact.affinity_type}</td>
                  <td>{contact.contacted ? "yes" : "no"}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}


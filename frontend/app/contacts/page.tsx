import { getCompanies, getContacts } from "../../lib/api";
import { ContactForm } from "./contact-form";
import { ContactList } from "./contact-list";

export const dynamic = "force-dynamic";

export default async function ContactsPage() {
  const [contactsResult, companiesResult] = await Promise.all([getContacts(), getCompanies()]);
  const contacts = contactsResult.data;
  const companies = companiesResult.data;

  return (
    <section>
      <h1>Contacts</h1>
      <p className="muted">
        Manual, fictional contacts only. No enrichment, scraping or outreach runs in this phase.
      </p>

      <ContactForm companies={companies} />

      {!contactsResult.ok ? (
        <p className="notice error">Could not load contacts: {contactsResult.error}</p>
      ) : null}
      {!companiesResult.ok ? (
        <p className="notice error">Could not load companies: {companiesResult.error}</p>
      ) : null}
      <ContactList contacts={contacts} companies={companies} />
    </section>
  );
}

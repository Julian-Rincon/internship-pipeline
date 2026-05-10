"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { Company, Contact } from "../../lib/api";

export function ContactList({ contacts, companies }: { contacts: Contact[]; companies: Company[] }) {
  const [query, setQuery] = useState("");
  const companyById = useMemo(() => new Map(companies.map((company) => [company.id, company])), [companies]);

  const filteredContacts = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) {
      return contacts;
    }

    return contacts.filter((contact) => {
      const company = companyById.get(contact.company_id);
      return [
        contact.full_name,
        contact.email,
        contact.role,
        contact.source,
        contact.affinity_type,
        company?.name,
        company?.domain
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(normalizedQuery);
    });
  }, [companyById, contacts, query]);

  return (
    <div className="panel table-wrap" style={{ marginTop: 16 }}>
      <label className="search-field">
        Search contacts
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search by name, company, role, source or affinity"
        />
      </label>
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
          {filteredContacts.length === 0 ? (
            <tr>
              <td colSpan={6} className="muted">
                No contacts match the current search.
              </td>
            </tr>
          ) : (
            filteredContacts.map((contact) => {
              const company = companyById.get(contact.company_id);
              return (
                <tr key={contact.id}>
                  <td>
                    <strong>{contact.full_name}</strong>
                    <br />
                    <span className="muted">{contact.email ?? "No email"}</span>
                  </td>
                  <td>{contact.role ?? "-"}</td>
                  <td>
                    {company ? (
                      <Link href={`/companies/${company.id}`}>{company.name}</Link>
                    ) : (
                      "Unknown company"
                    )}
                  </td>
                  <td>{contact.source}</td>
                  <td>{contact.affinity_type}</td>
                  <td>{contact.contacted ? "yes" : "no"}</td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}

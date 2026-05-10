"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { Company } from "../../lib/api";

export function CompanyList({ companies }: { companies: Company[] }) {
  const [query, setQuery] = useState("");

  const filteredCompanies = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) {
      return companies;
    }

    return companies.filter((company) =>
      [
        company.name,
        company.domain,
        company.tier,
        company.country,
        company.region,
        company.status
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(normalizedQuery)
    );
  }, [companies, query]);

  return (
    <div className="panel table-wrap" style={{ marginTop: 16 }}>
      <label className="search-field">
        Search companies
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search by name, domain, country, region or status"
        />
      </label>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Tier</th>
            <th>Country</th>
            <th>Careers</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {filteredCompanies.length === 0 ? (
            <tr>
              <td colSpan={5} className="muted">
                No companies match the current search.
              </td>
            </tr>
          ) : (
            filteredCompanies.map((company) => (
              <tr key={company.id}>
                <td>
                  <Link href={`/companies/${company.id}`}>
                    <strong>{company.name}</strong>
                  </Link>
                  <br />
                  <span className="muted">{company.domain ?? "No domain"}</span>
                </td>
                <td>{company.tier ?? "-"}</td>
                <td>{company.country ?? "-"}</td>
                <td>
                  {company.careers_url ? (
                    <a href={company.careers_url} target="_blank" rel="noreferrer">
                      Careers
                    </a>
                  ) : (
                    "-"
                  )}
                </td>
                <td>{company.status}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

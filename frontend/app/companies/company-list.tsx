"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { Company, User } from "../../lib/api";

const ownershipStatuses: Company["ownership_status"][] = ["unclaimed", "claimed", "paused", "done"];

export function CompanyList({ companies, users }: { companies: Company[]; users: User[] }) {
  const [query, setQuery] = useState("");
  const [ownershipFilter, setOwnershipFilter] = useState("");
  const userById = useMemo(() => new Map(users.map((user) => [user.id, user])), [users]);

  const filteredCompanies = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    return companies.filter((company) => {
      const ownerName = company.owner_user_id ? userById.get(company.owner_user_id)?.name : null;
      const matchesOwnership = !ownershipFilter || company.ownership_status === ownershipFilter;
      const matchesQuery =
        !normalizedQuery ||
        [
          company.name,
          company.domain,
          company.tier,
          company.country,
          company.region,
          company.status,
          company.ownership_status,
          ownerName
        ]
          .filter(Boolean)
          .join(" ")
          .toLowerCase()
          .includes(normalizedQuery);

      return matchesOwnership && matchesQuery;
    });
  }, [companies, ownershipFilter, query, userById]);

  return (
    <div className="panel table-wrap" style={{ marginTop: 16 }}>
      <div className="toolbar">
        <label>
          Search companies
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search by name, domain, country, region, owner or status"
          />
        </label>
        <label>
          Ownership
          <select value={ownershipFilter} onChange={(event) => setOwnershipFilter(event.target.value)}>
            <option value="">All</option>
            {ownershipStatuses.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </label>
      </div>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Tier</th>
            <th>Country</th>
            <th>Careers</th>
            <th>Status</th>
            <th>Owner</th>
            <th>Ownership</th>
          </tr>
        </thead>
        <tbody>
          {filteredCompanies.length === 0 ? (
            <tr>
              <td colSpan={7} className="muted">
                No companies match the current filters.
              </td>
            </tr>
          ) : (
            filteredCompanies.map((company) => {
              const owner = company.owner_user_id ? userById.get(company.owner_user_id) : null;
              return (
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
                  <td>{owner?.name ?? "-"}</td>
                  <td>
                    <span className={`badge badge-${company.ownership_status}`}>
                      {company.ownership_status}
                    </span>
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}

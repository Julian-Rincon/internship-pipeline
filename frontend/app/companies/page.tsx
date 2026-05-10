import { CompanyForm } from "./company-form";
import { getCompanies } from "../../lib/api";

export const dynamic = "force-dynamic";

export default async function CompaniesPage() {
  const result = await getCompanies();
  const companies = result.data;

  return (
    <section>
      <h1>Companies</h1>
      <p className="muted">Manual watchlist base. No scraping or enrichment runs in this phase.</p>

      <CompanyForm />

      <div className="panel table-wrap" style={{ marginTop: 16 }}>
        {!result.ok ? <p className="notice error">Could not load companies: {result.error}</p> : null}
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
            {companies.length === 0 ? (
              <tr>
                <td colSpan={5} className="muted">
                  No companies yet.
                </td>
              </tr>
            ) : (
              companies.map((company) => (
                <tr key={company.id}>
                  <td>
                    <strong>{company.name}</strong>
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
    </section>
  );
}

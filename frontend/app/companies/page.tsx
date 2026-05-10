import { CompanyForm } from "./company-form";
import { CompanyList } from "./company-list";
import { getCompanies, getUsers } from "../../lib/api";

export const dynamic = "force-dynamic";

export default async function CompaniesPage() {
  const [result, usersResult] = await Promise.all([getCompanies(), getUsers()]);
  const companies = result.data;

  return (
    <section>
      <h1>Companies</h1>
      <p className="muted">Manual watchlist base. No scraping or enrichment runs in this phase.</p>

      <CompanyForm />

      {!result.ok ? <p className="notice error">Could not load companies: {result.error}</p> : null}
      {!usersResult.ok ? <p className="notice error">Could not load owners: {usersResult.error}</p> : null}
      <CompanyList companies={companies} users={usersResult.data} />
    </section>
  );
}

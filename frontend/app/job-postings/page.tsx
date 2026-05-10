import { JobPostingsClient } from "./job-postings-client";
import { getCompanies, getJobPostings, getUsers } from "../../lib/api";

export const dynamic = "force-dynamic";

export default async function JobPostingsPage() {
  const [jobPostingsResult, companiesResult, usersResult] = await Promise.all([
    getJobPostings(),
    getCompanies(),
    getUsers()
  ]);

  return (
    <section>
      <h1>Job Postings</h1>
      <p className="muted">
        Reviewed opportunities can be linked to companies and turned into manual applications. No
        outreach or external sending happens here.
      </p>

      {!jobPostingsResult.ok ? (
        <p className="notice error">Could not load job postings: {jobPostingsResult.error}</p>
      ) : null}
      {!companiesResult.ok ? (
        <p className="notice error">Could not load companies: {companiesResult.error}</p>
      ) : null}
      {!usersResult.ok ? <p className="notice error">Could not load users: {usersResult.error}</p> : null}

      <JobPostingsClient
        jobPostings={jobPostingsResult.data}
        companies={companiesResult.data}
        users={usersResult.data}
      />
    </section>
  );
}

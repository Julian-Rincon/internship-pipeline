import Link from "next/link";
import { SourceManager } from "./source-manager";
import { getDiscoverySources } from "../../../lib/api";

export const dynamic = "force-dynamic";

export default async function DiscoverySourcesPage() {
  const result = await getDiscoverySources();

  return (
    <section>
      <div className="breadcrumb-row">
        <Link href="/discovery">Discovery</Link>
      </div>
      <h1>Discovery sources</h1>
      <p className="muted">
        Controlled public ATS source intake for Greenhouse, Lever and Ashby only. Jobs become pending
        discovery candidates and still require human review.
      </p>

      {!result.ok ? <p className="notice error">Could not load sources: {result.error}</p> : null}
      <SourceManager sources={result.data} />
    </section>
  );
}

import { getVisaData, type VisaData } from "../../lib/api";
import { VisaForm } from "./visa-form";

export const dynamic = "force-dynamic";

const friendlyBadge: Record<string, string> = {
  green: "badge badge-green",
  yellow: "badge badge-yellow",
  red: "badge badge-red",
  unknown: "badge",
};

function groupByInternFriendly(visaData: VisaData[]): Record<string, VisaData[]> {
  const order = ["green", "yellow", "red", "unknown"];
  const groups: Record<string, VisaData[]> = {};
  for (const status of order) {
    groups[status] = [];
  }
  for (const entry of visaData) {
    const key = entry.intern_friendly ?? "unknown";
    if (!groups[key]) groups[key] = [];
    groups[key].push(entry);
  }
  return groups;
}

export default async function VisaPage() {
  const visaResult = await getVisaData();
  const visaData = visaResult.data;
  const groups = groupByInternFriendly(visaData);
  const order = ["green", "yellow", "red", "unknown"] as const;

  return (
    <section>
      <h1>Visa & Sponsorship Filter</h1>
      <p className="muted">
        Track visa sponsorship status and intern-friendliness per company and country.
      </p>

      <VisaForm />

      {!visaResult.ok ? (
        <p className="notice error">Could not load visa data: {visaResult.error}</p>
      ) : null}

      {order.map((status) => {
        const entries = groups[status];
        if (entries.length === 0) return null;
        return (
          <div key={status} className="panel" style={{ marginTop: "20px" }}>
            <h2>
              <span className={friendlyBadge[status]}>{status}</span>
              {" "}
              <span style={{ fontWeight: 400, fontSize: "13px", color: "var(--muted)" }}>
                ({entries.length} {entries.length === 1 ? "entry" : "entries"})
              </span>
            </h2>
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Company</th>
                    <th>Country</th>
                    <th>Visa type</th>
                    <th>Sponsor verified</th>
                    <th>Last verified</th>
                    <th>Evidence</th>
                    <th>Notes</th>
                  </tr>
                </thead>
                <tbody>
                  {entries.map((entry) => (
                    <tr key={entry.id}>
                      <td>
                        <span className="muted" style={{ fontFamily: "monospace", fontSize: "11px" }}>
                          {entry.company_id.slice(0, 8)}…
                        </span>
                      </td>
                      <td>{entry.country}</td>
                      <td className="muted">{entry.visa_type ?? "—"}</td>
                      <td>
                        <span className={entry.sponsor_verified ? "badge badge-green" : "badge"}>
                          {entry.sponsor_verified ? "yes" : "no"}
                        </span>
                      </td>
                      <td className="muted">{entry.last_verified ?? "—"}</td>
                      <td>
                        {entry.evidence_url ? (
                          <a href={entry.evidence_url} target="_blank" rel="noopener noreferrer">
                            link
                          </a>
                        ) : (
                          <span className="muted">—</span>
                        )}
                      </td>
                      <td className="muted">{entry.notes ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );
      })}

      {visaData.length === 0 && visaResult.ok ? (
        <div className="panel" style={{ marginTop: "20px" }}>
          <p className="muted">No visa data recorded yet.</p>
        </div>
      ) : null}
    </section>
  );
}

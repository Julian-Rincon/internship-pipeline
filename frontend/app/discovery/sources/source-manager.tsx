"use client";

import { FormEvent, useState } from "react";
import {
  createDiscoverySource,
  deleteDiscoverySource,
  runDiscoverySource,
  runEnabledDiscoverySources,
  updateDiscoverySource,
  type DiscoverySource,
  type DiscoverySourcePayload,
  type DiscoverySourceRunResult
} from "../../../lib/api";

const sourceTypes: DiscoverySource["source_type"][] = ["greenhouse", "lever", "ashby"];

function nullableValue(formData: FormData, name: string) {
  const value = formData.get(name)?.toString().trim();
  return value ? value : null;
}

function reload() {
  window.location.reload();
}

function RunSummary({ result }: { result: DiscoverySourceRunResult }) {
  return (
    <div className="notice">
      <strong>{result.source_name}</strong>: fetched {result.fetched_count}, internship-like{" "}
      {result.internship_like_count}, candidates created {result.candidates_created}, skipped{" "}
      {result.candidates_skipped}, job postings created {result.job_postings_created}
      {result.errors.length > 0 ? <span> Errors: {result.errors.join("; ")}</span> : null}
    </div>
  );
}

export function SourceManager({ sources }: { sources: DiscoverySource[] }) {
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<DiscoverySourceRunResult[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const formData = new FormData(event.currentTarget);
    const payload: DiscoverySourcePayload = {
      name: formData.get("name")?.toString().trim() ?? "",
      source_type: formData.get("source_type")?.toString() as DiscoverySource["source_type"],
      source_key: formData.get("source_key")?.toString().trim() ?? "",
      company_hint: nullableValue(formData, "company_hint"),
      country: nullableValue(formData, "country"),
      region: nullableValue(formData, "region"),
      enabled: formData.get("enabled") === "on"
    };

    try {
      await createDiscoverySource(payload);
      reload();
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : "Could not create source");
      setIsSubmitting(false);
    }
  }

  async function onToggle(source: DiscoverySource) {
    setError(null);
    try {
      await updateDiscoverySource(source.id, { enabled: !source.enabled });
      reload();
    } catch (updateError) {
      setError(updateError instanceof Error ? updateError.message : "Could not update source");
    }
  }

  async function onDelete(source: DiscoverySource) {
    if (!window.confirm("Delete this discovery source?")) {
      return;
    }

    setError(null);
    try {
      await deleteDiscoverySource(source.id);
      reload();
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Could not delete source");
    }
  }

  async function onRun(source: DiscoverySource) {
    setError(null);
    setResults([]);
    try {
      const result = await runDiscoverySource(source.id);
      setResults([result]);
    } catch (runError) {
      setError(runError instanceof Error ? runError.message : "Could not run source");
    }
  }

  async function onRunEnabled() {
    setError(null);
    setResults([]);
    try {
      const runResults = await runEnabledDiscoverySources();
      setResults(runResults);
    } catch (runError) {
      setError(runError instanceof Error ? runError.message : "Could not run enabled sources");
    }
  }

  return (
    <>
      <div className="panel">
        <h2>Add source</h2>
        {error ? <p className="notice error">{error}</p> : null}
        <form className="form" onSubmit={onCreate}>
          <div className="form-grid">
            <label>
              Name
              <input name="name" required />
            </label>
            <label>
              Type
              <select name="source_type" defaultValue="greenhouse">
                {sourceTypes.map((sourceType) => (
                  <option key={sourceType} value={sourceType}>
                    {sourceType}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Source key
              <input name="source_key" required placeholder="board token, Lever site or Ashby board name" />
            </label>
            <label>
              Company hint
              <input name="company_hint" />
            </label>
            <label>
              Country
              <input name="country" />
            </label>
            <label>
              Region
              <input name="region" />
            </label>
            <label className="checkbox-label">
              <input name="enabled" type="checkbox" defaultChecked />
              Enabled
            </label>
          </div>
          <button type="submit" disabled={isSubmitting}>
            Create source
          </button>
        </form>
      </div>

      <div className="panel" style={{ marginTop: 16 }}>
        <div className="button-row">
          <button type="button" onClick={onRunEnabled}>
            Run all enabled
          </button>
        </div>
        {results.length > 0 ? (
          <div className="discovery-stack">
            {results.map((result) => (
              <RunSummary result={result} key={result.source_id} />
            ))}
          </div>
        ) : null}
      </div>

      <div className="panel table-wrap" style={{ marginTop: 16 }}>
        <h2>Sources</h2>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Key</th>
              <th>Enabled</th>
              <th>Last run</th>
              <th>Status</th>
              <th>Error</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sources.length === 0 ? (
              <tr>
                <td colSpan={8} className="muted">
                  No discovery sources yet.
                </td>
              </tr>
            ) : (
              sources.map((source) => (
                <tr key={source.id}>
                  <td>
                    <strong>{source.name}</strong>
                    <br />
                    <span className="muted">{source.company_hint ?? "-"}</span>
                  </td>
                  <td>{source.source_type}</td>
                  <td>{source.source_key}</td>
                  <td>{source.enabled ? "yes" : "no"}</td>
                  <td>{source.last_run_at ?? "-"}</td>
                  <td>{source.last_status ?? "-"}</td>
                  <td>{source.last_error ?? "-"}</td>
                  <td>
                    <div className="button-row">
                      <button type="button" onClick={() => onRun(source)} disabled={!source.enabled}>
                        Run
                      </button>
                      <button type="button" onClick={() => onToggle(source)}>
                        {source.enabled ? "Disable" : "Enable"}
                      </button>
                      <button className="danger-button" type="button" onClick={() => onDelete(source)}>
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}

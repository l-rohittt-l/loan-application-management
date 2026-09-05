// The manager's activity view (D-11): who did what, human or AI, with filters.

import { useEffect, useState } from "react";
import { api, errorMessage } from "../api/client";
import ErrorBanner from "../components/ErrorBanner";
import Spinner from "../components/Spinner";
import { formatDateTime, label } from "../utils/format";

const ENTITY_TYPES = ["application", "applicant", "document", "user"];
const empty = { actor_id: "", actor_type: "", action: "", entity_type: "", entity_id: "", from_date: "", to_date: "" };

export default function Activity() {
  const [filters, setFilters] = useState(empty);
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const limit = 50;

  useEffect(() => {
    const params = { page, limit };
    for (const [k, v] of Object.entries(filters)) if (v) params[k] = v;
    api.get("/activity", { params }).then((r) => { setData(r.data); setError(""); }).catch((err) => setError(errorMessage(err)));
  }, [filters, page]);

  const set = (f) => (e) => { setPage(1); setFilters({ ...filters, [f]: e.target.value }); };
  const pages = data ? Math.max(1, Math.ceil(data.total_count / limit)) : 1;

  return (
    <>
      <div className="page-head"><h1>Activity</h1></div>
      <div className="filters">
        <label>Who<input value={filters.actor_id} onChange={set("actor_id")} placeholder="email or agent name" /></label>
        <label>Kind<select value={filters.actor_type} onChange={set("actor_type")}><option value="">Any</option><option value="human">Human</option><option value="ai">AI</option></select></label>
        <label>Action<input value={filters.action} onChange={set("action")} placeholder="e.g. status_changed" /></label>
        <label>Record type<select value={filters.entity_type} onChange={set("entity_type")}><option value="">Any</option>{ENTITY_TYPES.map((t) => <option key={t} value={t}>{label(t)}</option>)}</select></label>
        <label>Record id<input type="number" min={1} value={filters.entity_id} onChange={set("entity_id")} style={{ width: 100 }} /></label>
        <label>From<input type="date" value={filters.from_date} onChange={set("from_date")} /></label>
        <label>To<input type="date" value={filters.to_date} onChange={set("to_date")} /></label>
        <button type="button" className="btn btn-ghost" onClick={() => { setPage(1); setFilters(empty); }}>Clear</button>
      </div>
      <ErrorBanner message={error} onClose={() => setError("")} />
      {!data ? <Spinner /> : (
        <>
          <div className="table-wrap">
            <table>
              <thead><tr><th>When</th><th>Who</th><th>Action</th><th>Record</th><th>Details</th><th>Request</th></tr></thead>
              <tbody>
                {data.items.length ? data.items.map((r) => (
                  <tr key={r.id}>
                    <td>{formatDateTime(r.created_at)}</td>
                    <td>
                      {r.actor_id}{r.actor_role && <span className="muted"> · {label(r.actor_role)}</span>}
                      {r.actor_type === "ai" && <> <span className="pill pill-ai">AI</span>{r.on_behalf_of && <span className="muted"> for {r.on_behalf_of}</span>}</>}
                    </td>
                    <td>{label(r.action)}</td>
                    <td>{r.entity_type ? `${label(r.entity_type)} #${r.entity_id}` : ""}</td>
                    <td><code className="small">{r.details || ""}</code></td>
                    <td><code className="small">{r.request_id || ""}</code></td>
                  </tr>
                )) : <tr><td colSpan={6} className="muted">Nothing matches.</td></tr>}
              </tbody>
            </table>
          </div>
          <div className="pager">
            <span className="muted">{data.total_count} total</span>
            <button type="button" className="btn btn-sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>‹ Prev</button>
            <span>Page {page} of {pages}</span>
            <button type="button" className="btn btn-sm" disabled={page >= pages} onClick={() => setPage(page + 1)}>Next ›</button>
          </div>
        </>
      )}
    </>
  );
}

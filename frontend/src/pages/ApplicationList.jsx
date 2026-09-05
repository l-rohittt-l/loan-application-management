// User story 09: the table with filters and the exact status colours.
// Staff see everything; an applicant's list is already limited to their own by the server.

import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, errorMessage } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import ErrorBanner from "../components/ErrorBanner";
import Spinner from "../components/Spinner";
import StatusBadge from "../components/StatusBadge";
import { formatDate, label, rupees } from "../utils/format";
import { LOAN_TYPES } from "../utils/validation";

const STATUSES = ["submitted", "under_review", "approved", "rejected", "disbursed"];

export default function ApplicationList() {
  const { isApplicant } = useAuth();
  const navigate = useNavigate();
  const [filters, setFilters] = useState({ status: "", loan_type: "", from_date: "", to_date: "" });
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const limit = 20;

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    const params = { page, limit };
    for (const [k, v] of Object.entries(filters)) if (v) params[k] = v;
    api
      .get("/applications", { params })
      .then((res) => { if (!cancelled) { setData(res.data); setError(""); } })
      .catch((err) => { if (!cancelled) setError(errorMessage(err)); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [filters, page]);

  const set = (field) => (e) => { setPage(1); setFilters({ ...filters, [field]: e.target.value }); };
  const pages = data ? Math.max(1, Math.ceil(data.total_count / limit)) : 1;

  return (
    <>
      <div className="page-head">
        <h1>{isApplicant ? "My applications" : "Applications"}</h1>
        <Link className="btn btn-primary" to="/applications/new">{isApplicant ? "Apply for a loan" : "New application"}</Link>
      </div>

      <div className="filters">
        <label>
          Status
          <select value={filters.status} onChange={set("status")}>
            <option value="">All</option>
            {STATUSES.map((s) => <option key={s} value={s}>{label(s)}</option>)}
          </select>
        </label>
        <label>
          Loan type
          <select value={filters.loan_type} onChange={set("loan_type")}>
            <option value="">All</option>
            {LOAN_TYPES.map((t) => <option key={t} value={t}>{label(t)}</option>)}
          </select>
        </label>
        <label>
          Submitted from
          <input type="date" value={filters.from_date} onChange={set("from_date")} />
        </label>
        <label>
          Submitted to
          <input type="date" value={filters.to_date} onChange={set("to_date")} />
        </label>
        {(filters.status || filters.loan_type || filters.from_date || filters.to_date) && (
          <button type="button" className="btn btn-ghost" onClick={() => { setPage(1); setFilters({ status: "", loan_type: "", from_date: "", to_date: "" }); }}>
            Clear
          </button>
        )}
      </div>

      <ErrorBanner message={error} onClose={() => setError("")} />
      {loading && !data ? (
        <Spinner />
      ) : (
        <>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th><th>Applicant</th><th>Loan type</th><th className="num">Amount</th>
                  <th className="num">Tenure</th><th>Status</th><th>Submitted</th>
                </tr>
              </thead>
              <tbody>
                {data?.items?.length ? data.items.map((a) => (
                  <tr key={a.id} className="row-link" onClick={() => navigate(`/applications/${a.id}`)}>
                    <td>#{a.id}</td>
                    <td>{a.applicant_name || `Applicant ${a.applicant_id}`}</td>
                    <td>{label(a.loan_type)}</td>
                    <td className="num">{rupees(a.amount_requested)}</td>
                    <td className="num">{a.tenure_months} mo</td>
                    <td><StatusBadge status={a.status} /></td>
                    <td>{formatDate(a.submitted_at)}</td>
                  </tr>
                )) : (
                  <tr><td colSpan={7} className="muted">No applications match.</td></tr>
                )}
              </tbody>
            </table>
          </div>
          <div className="pager">
            <span className="muted">{data?.total_count ?? 0} total</span>
            <button type="button" className="btn btn-sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>‹ Prev</button>
            <span>Page {page} of {pages}</span>
            <button type="button" className="btn btn-sm" disabled={page >= pages} onClick={() => setPage(page + 1)}>Next ›</button>
          </div>
        </>
      )}
    </>
  );
}

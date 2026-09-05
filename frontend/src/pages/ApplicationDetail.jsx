// User story 11: everything about one application. The timeline, the documents,
// and for staff, the update-status control. A manager also sees the activity trail.

import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, errorMessage } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import DocumentChecklist from "../components/DocumentChecklist";
import ErrorBanner from "../components/ErrorBanner";
import Spinner from "../components/Spinner";
import StatusBadge from "../components/StatusBadge";
import Timeline from "../components/Timeline";
import { formatDate, formatDateTime, label, rupees } from "../utils/format";

// Mirrors VALID_TRANSITIONS in backend/app/domain/rules.py. The server still decides.
const NEXT = {
  submitted: ["under_review"],
  under_review: ["approved", "rejected"],
  approved: ["disbursed"],
  rejected: [],
  disbursed: [],
};
const MANAGER_ONLY = new Set(["disbursed"]);

export default function ApplicationDetail() {
  const { id } = useParams();
  const { isStaff, isManager } = useAuth();
  const [app, setApp] = useState(null);
  const [docs, setDocs] = useState(null);
  const [activity, setActivity] = useState([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(true);
  const [newStatus, setNewStatus] = useState("");
  const [remarks, setRemarks] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const [a, d] = await Promise.all([
        api.get(`/applications/${id}`),
        api.get(`/applications/${id}/documents`),
      ]);
      setApp(a.data);
      setDocs(d.data);
      if (isManager) {
        const act = await api.get(`/activity/entity/application/${id}`);
        setActivity(act.data);
      }
      setError("");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [id, isManager]);

  useEffect(() => { load(); }, [load]);

  async function updateStatus(e) {
    e.preventDefault();
    if (!newStatus) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api.patch(`/applications/${id}/status`, { new_status: newStatus, remarks: remarks || null });
      setNotice(`Status changed to ${label(newStatus)}.`);
      setNewStatus("");
      setRemarks("");
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <Spinner text="Loading application…" />;
  if (!app) return <ErrorBanner message={error || "Not found."} />;

  const options = (NEXT[app.status] || []).filter((s) => isManager || !MANAGER_ONLY.has(s));
  const managerNeeded = (NEXT[app.status] || []).some((s) => MANAGER_ONLY.has(s)) && !isManager;

  return (
    <>
      <div className="page-head">
        <div>
          <Link to="/applications" className="muted">‹ Back to applications</Link>
          <h1 style={{ marginTop: "0.25rem" }}>
            Application #{app.id} <StatusBadge status={app.status} />
          </h1>
        </div>
      </div>
      <ErrorBanner message={error} onClose={() => setError("")} />
      {notice && <div className="banner banner-ok">{notice}</div>}

      <div className="detail-grid">
        <div>
          <div className="card">
            <h2 style={{ marginTop: 0 }}>Loan</h2>
            <dl className="kv">
              <dt>Loan type</dt><dd>{label(app.loan_type)}</dd>
              <dt>Amount</dt><dd>{rupees(app.amount_requested)}</dd>
              <dt>Tenure</dt><dd>{app.tenure_months} months</dd>
              <dt>Purpose</dt><dd>{app.purpose}</dd>
              <dt>Submitted</dt><dd>{formatDateTime(app.submitted_at)}</dd>
              <dt>Last updated</dt><dd>{formatDateTime(app.updated_at)}</dd>
            </dl>

            {app.applicant && (
              <>
                <h2>Applicant</h2>
                <dl className="kv">
                  <dt>Name</dt><dd>{app.applicant.name}</dd>
                  <dt>Email</dt><dd>{app.applicant.email}</dd>
                  <dt>Phone</dt><dd>{app.applicant.phone}</dd>
                  <dt>Employment</dt><dd>{label(app.applicant.employment_status)}</dd>
                  <dt>Annual income</dt><dd>{rupees(app.applicant.annual_income)}</dd>
                  <dt>CIBIL score</dt><dd>{app.applicant.credit_score ?? <span className="muted">not provided</span>}</dd>
                  <dt>Date of birth</dt><dd>{app.applicant.date_of_birth ? formatDate(app.applicant.date_of_birth) : <span className="muted">not provided</span>}</dd>
                  <dt>Existing EMIs</dt><dd>{rupees(app.applicant.existing_monthly_emi)} / month</dd>
                </dl>
              </>
            )}
          </div>

          <div className="card" style={{ marginTop: "1.25rem" }}>
            <h2 style={{ marginTop: 0 }}>Documents</h2>
            <DocumentChecklist applicationId={app.id} data={docs} onChange={load} />
          </div>

          {isManager && (
            <div className="card" style={{ marginTop: "1.25rem" }}>
              <h2 style={{ marginTop: 0 }}>Activity on this application</h2>
              {activity.length === 0 ? <p className="muted">Nothing recorded.</p> : (
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>When</th><th>Who</th><th>What</th></tr></thead>
                    <tbody>
                      {activity.map((row) => (
                        <tr key={row.id}>
                          <td>{formatDateTime(row.created_at)}</td>
                          <td>
                            {row.actor_id}
                            {row.actor_type === "ai" && <> <span className="pill pill-ai">AI</span>{row.on_behalf_of && <span className="muted"> for {row.on_behalf_of}</span>}</>}
                          </td>
                          <td>{label(row.action)}{row.details && <> <code className="small">{row.details}</code></>}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>

        <div>
          <div className="card">
            <h2 style={{ marginTop: 0 }}>Status history</h2>
            <Timeline history={app.status_history} />
          </div>

          {isStaff && (
            <div className="card" style={{ marginTop: "1.25rem" }}>
              <h2 style={{ marginTop: 0 }}>Update status</h2>
              {options.length === 0 ? (
                <p className="muted">
                  {managerNeeded ? "Only a branch manager can disburse this loan." : "This application is closed."}
                </p>
              ) : (
                <form onSubmit={updateStatus} noValidate>
                  <label>
                    Move to
                    <select value={newStatus} onChange={(e) => setNewStatus(e.target.value)}>
                      <option value="">Choose…</option>
                      {options.map((s) => <option key={s} value={s}>{label(s)}</option>)}
                    </select>
                  </label>
                  <label>
                    Remarks
                    <textarea rows={3} maxLength={1000} value={remarks} onChange={(e) => setRemarks(e.target.value)} placeholder={newStatus === "rejected" ? "The reason is shown to the applicant" : "Optional"} />
                  </label>
                  <button type="submit" className="btn btn-primary" disabled={busy || !newStatus}>
                    {busy ? "Saving…" : "Update status"}
                  </button>
                </form>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

// User story 10: the submission form. Client-side checks first, then the
// eligibility check (D-01), then submit. A failed eligibility check warns
// and explains; it never blocks, because the server's rule is advisory too.

import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { api, errorMessage } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import ErrorBanner from "../components/ErrorBanner";
import Spinner from "../components/Spinner";
import { label, rupees } from "../utils/format";
import { LOAN_TYPES, TENURE_LIMITS, checkAmount, checkPurpose, checkTenure, collect } from "../utils/validation";

export default function NewApplication() {
  const { isApplicant } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  // If staff just created a borrower profile, that page sends us the new id.
  const preselected = location.state?.applicantId ? String(location.state.applicantId) : "";
  const [applicants, setApplicants] = useState([]);   // staff: who to apply for
  const [me, setMe] = useState(null);                 // applicant: own profile
  const [form, setForm] = useState({ applicant_id: preselected, loan_type: "personal", amount_requested: "", tenure_months: "", purpose: "" });
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [check, setCheck] = useState(null);           // the eligibility answer
  const [checkedFor, setCheckedFor] = useState("");   // which inputs the answer is for
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = isApplicant
      ? api.get("/applicants/me").then((r) => { setMe(r.data); setForm((f) => ({ ...f, applicant_id: String(r.data.id) })); })
      : api.get("/applicants", { params: { limit: 100 } }).then((r) => setApplicants(r.data.items));
    load.catch((err) => setError(errorMessage(err))).finally(() => setLoading(false));
  }, [isApplicant]);

  const set = (field) => (e) => { setForm({ ...form, [field]: e.target.value }); setCheck(null); };

  function validate() {
    const found = collect({
      applicant_id: form.applicant_id ? "" : "Choose an applicant",
      amount_requested: checkAmount(form.amount_requested, form.loan_type),
      tenure_months: checkTenure(form.tenure_months, form.loan_type),
      purpose: checkPurpose(form.purpose),
    });
    setErrors(found);
    return Object.keys(found).length === 0;
  }

  const payload = () => ({
    applicant_id: Number(form.applicant_id),
    loan_type: form.loan_type,
    amount_requested: Number(form.amount_requested),
    tenure_months: Number(form.tenure_months),
  });
  const fingerprint = () => JSON.stringify(payload());

  async function runCheck() {
    if (!validate()) return null;
    setBusy(true);
    setError("");
    try {
      const res = await api.post("/applications/check-eligibility", payload());
      setCheck(res.data);
      setCheckedFor(fingerprint());
      return res.data;
    } catch (err) {
      setError(errorMessage(err));
      return null;
    } finally {
      setBusy(false);
    }
  }

  async function submit(force = false) {
    if (!validate()) return;
    // Always check first. If the answer is "not eligible" and the user has not
    // said "submit anyway", stop here and show the reasons.
    let result = checkedFor === fingerprint() ? check : null;
    if (!result) result = await runCheck();
    if (!result) return;
    if (!result.eligible && !force) return;

    setBusy(true);
    setError("");
    try {
      const res = await api.post("/applications", { ...payload(), purpose: form.purpose.trim() });
      navigate(`/applications/${res.data.id}`);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  const applySuggestion = (field, value) => { setForm({ ...form, [field]: String(value) }); setCheck(null); };
  const [lo, hi] = TENURE_LIMITS[form.loan_type];

  if (loading) return <Spinner />;

  return (
    <>
      <div className="page-head">
        <h1>{isApplicant ? "Apply for a loan" : "New application"}</h1>
      </div>
      <ErrorBanner message={error} onClose={() => setError("")} />

      <div className="detail-grid">
        <div className="card">
          <form onSubmit={(e) => { e.preventDefault(); submit(false); }} noValidate>
            {isApplicant ? (
              <p className="muted">Applying as <strong>{me?.name}</strong> ({me?.email}). <Link to="/profile">View profile</Link></p>
            ) : (
              <label>
                Applicant
                <select value={form.applicant_id} onChange={set("applicant_id")}>
                  <option value="">Choose…</option>
                  {applicants.map((a) => <option key={a.id} value={a.id}>{a.name} · {a.email}</option>)}
                </select>
                {errors.applicant_id && <span className="field-error">{errors.applicant_id}</span>}
                <span className="hint">Not listed? <Link to="/applicants/new">Create a borrower profile</Link></span>
              </label>
            )}

            <label>
              Loan type
              <select value={form.loan_type} onChange={set("loan_type")}>
                {LOAN_TYPES.map((t) => <option key={t} value={t}>{label(t)}</option>)}
              </select>
            </label>
            <label>
              Amount (₹)
              <input type="number" min={10000} step={1000} value={form.amount_requested} onChange={set("amount_requested")} placeholder="e.g. 500000" />
              {errors.amount_requested && <span className="field-error">{errors.amount_requested}</span>}
            </label>
            <label>
              Tenure (months)
              <input type="number" min={lo} max={hi} value={form.tenure_months} onChange={set("tenure_months")} placeholder={`${lo} to ${hi}`} />
              {errors.tenure_months && <span className="field-error">{errors.tenure_months}</span>}
              <span className="hint">{label(form.loan_type)} loans run {lo} to {hi} months.</span>
            </label>
            <label>
              Purpose
              <textarea rows={3} maxLength={500} value={form.purpose} onChange={set("purpose")} placeholder="What is the loan for?" />
              {errors.purpose && <span className="field-error">{errors.purpose}</span>}
            </label>

            <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
              <button type="button" className="btn" disabled={busy} onClick={runCheck}>Check eligibility</button>
              <button type="submit" className="btn btn-primary" disabled={busy}>{busy ? "Working…" : "Submit application"}</button>
            </div>
          </form>
        </div>

        <div>
          {check && (
            <div className={`card`}>
              <h2 style={{ marginTop: 0 }}>{check.eligible ? "Looks good" : "Not eligible as entered"}</h2>
              <dl className="kv">
                <dt>Estimated EMI</dt><dd>{rupees(check.estimated_emi)} / month</dd>
                <dt>Room for EMIs</dt><dd>{rupees(check.max_affordable_emi)} / month</dd>
              </dl>
              {check.problems.length > 0 && (
                <ul>
                  {check.problems.map((p, i) => <li key={i}>{p}</li>)}
                </ul>
              )}
              {(check.suggested_amount || check.suggested_tenure_months) && (
                <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginTop: "0.5rem" }}>
                  {check.suggested_amount && (
                    <button type="button" className="btn btn-sm" onClick={() => applySuggestion("amount_requested", Math.round(check.suggested_amount))}>
                      Use {rupees(check.suggested_amount)}
                    </button>
                  )}
                  {check.suggested_tenure_months && (
                    <button type="button" className="btn btn-sm" onClick={() => applySuggestion("tenure_months", check.suggested_tenure_months)}>
                      Use {check.suggested_tenure_months} months
                    </button>
                  )}
                </div>
              )}
              {!check.eligible && (
                <div className="banner banner-warn" style={{ marginTop: "1rem", marginBottom: 0 }}>
                  <span>You can still submit, but it is likely to be rejected or sent back for more information.</span>
                </div>
              )}
              {!check.eligible && (
                <button type="button" className="btn btn-danger" style={{ marginTop: "0.75rem" }} disabled={busy} onClick={() => submit(true)}>
                  Submit anyway
                </button>
              )}
            </div>
          )}
          {!check && (
            <div className="card">
              <h2 style={{ marginTop: 0 }}>Before you submit</h2>
              <p className="muted">
                Check eligibility to see the estimated EMI and whether the amount, tenure, income, credit score and age fit the bank's rules for this loan type.
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

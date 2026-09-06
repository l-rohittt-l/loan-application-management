// User story 10: the submission form. Client-side checks first, then the
// eligibility check (D-01), then submit. A failed eligibility check warns
// and explains; it never blocks, because the server's rule is advisory too.
//
// Piece 18 reshaped this page. It used to be one long stack of inputs with no
// sense of where you were. It is now three labelled sections — who is applying,
// the loan, and why — so the form reads like a conversation rather than a pile
// of boxes. Every field states its rule quietly until it is broken.
//
// The eligibility panel beside it still works exactly as before. Making the
// check run on its own, and the assessment card that goes with it, is Piece 19.

import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { api, errorMessage } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import ErrorBanner from "../components/ErrorBanner";
import Spinner from "../components/Spinner";
import Button from "../components/ui/Button";
import Icon from "../components/ui/Icon";
import { label, rupees } from "../utils/format";
import {
  AMOUNT_LIMITS, LOAN_TYPES, TENURE_LIMITS,
  checkAmount, checkPurpose, checkTenure, collect,
} from "../utils/validation";

// The terms people actually pick, per loan type. Saves typing and quietly
// teaches what a sensible tenure looks like for that kind of loan.
const COMMON_TENURES = {
  personal: [12, 24, 36, 48, 60],
  home: [120, 180, 240, 300, 360],
  auto: [12, 24, 36, 60, 84],
};

// A word about what each loan is for, shown under the loan type.
const LOAN_BLURB = {
  personal: "Unsecured, for any purpose. Shorter terms and a higher rate.",
  home: "Secured against the property. The longest terms we offer.",
  auto: "Secured against the vehicle. Needs a dealer quotation later.",
};

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
  const pickTenure = (months) => { setForm({ ...form, tenure_months: String(months) }); setCheck(null); };

  const [lo, hi] = TENURE_LIMITS[form.loan_type];
  const cap = AMOUNT_LIMITS[form.loan_type];
  const amountNumber = Number(form.amount_requested);
  const showAmountPreview = form.amount_requested !== "" && amountNumber > 0;
  const purposeLeft = 500 - form.purpose.length;

  if (loading) return <Spinner text="Loading…" />;

  return (
    <>
      <div className="page-head">
        <div>
          <h1>{isApplicant ? "Apply for a loan" : "New application"}</h1>
          <p className="sub">
            Check eligibility before submitting — it takes a second and tells you
            what to adjust if anything is out of range.
          </p>
        </div>
      </div>
      <ErrorBanner message={error} onClose={() => setError("")} />

      <div className="detail-grid">
        <div className="card">
          <form onSubmit={(e) => { e.preventDefault(); submit(false); }} noValidate>

            {/* ---------------------------------------------- who is applying */}
            <div className="form-section">
              <p className="form-section-title">Who is applying</p>
              {isApplicant ? (
                <p className="muted" style={{ margin: 0 }}>
                  Applying as <strong>{me?.name}</strong> ({me?.email}). <Link to="/profile">View profile</Link>
                </p>
              ) : (
                <label>
                  Applicant
                  <select value={form.applicant_id} onChange={set("applicant_id")}>
                    <option value="">Choose…</option>
                    {applicants.map((a) => <option key={a.id} value={a.id}>{a.name} · {a.email}</option>)}
                  </select>
                  {errors.applicant_id
                    ? <span className="field-error">{errors.applicant_id}</span>
                    : <span className="hint">Not listed? <Link to="/applicants/new">Create a borrower profile</Link></span>}
                </label>
              )}
            </div>

            {/* ------------------------------------------------------ the loan */}
            <div className="form-section">
              <p className="form-section-title">The loan</p>

              <label>
                Loan type
                <select value={form.loan_type} onChange={set("loan_type")}>
                  {LOAN_TYPES.map((t) => <option key={t} value={t}>{label(t)}</option>)}
                </select>
                <span className="hint">{LOAN_BLURB[form.loan_type]}</span>
              </label>

              <label>
                Amount (₹)
                <input
                  type="number" min={10000} step={1000} inputMode="numeric"
                  value={form.amount_requested} onChange={set("amount_requested")}
                  placeholder="e.g. 500000"
                />
                {errors.amount_requested ? (
                  <span className="field-error">{errors.amount_requested}</span>
                ) : showAmountPreview ? (
                  // A row of digits is hard to read, and this is the field people
                  // get wrong. Writing it out as you type removes the doubt.
                  <span className="amount-preview">{rupees(amountNumber)}</span>
                ) : (
                  <span className="hint">
                    Between ₹10,000 and {rupees(cap)} for a {label(form.loan_type).toLowerCase()} loan.
                  </span>
                )}
              </label>

              <label>
                Tenure (months)
                <input
                  type="number" min={lo} max={hi} inputMode="numeric"
                  value={form.tenure_months} onChange={set("tenure_months")}
                  placeholder={`${lo} to ${hi}`}
                />
                {errors.tenure_months
                  ? <span className="field-error">{errors.tenure_months}</span>
                  : <span className="hint">{label(form.loan_type)} loans run {lo} to {hi} months.</span>}
              </label>

              <div className="chips" role="group" aria-label="Common tenures">
                {COMMON_TENURES[form.loan_type].map((months) => (
                  <button
                    key={months}
                    type="button"
                    className={`chip ${Number(form.tenure_months) === months ? "chip-on" : ""}`}
                    onClick={() => pickTenure(months)}
                  >
                    {months % 12 === 0 ? `${months / 12} yr` : `${months} mo`}
                  </button>
                ))}
              </div>
            </div>

            {/* ------------------------------------------------ why the loan */}
            <div className="form-section">
              <p className="form-section-title">Why you need it</p>
              <label>
                Purpose
                <textarea rows={3} maxLength={500} value={form.purpose} onChange={set("purpose")}
                          placeholder="What is the loan for? A sentence is enough." />
                {errors.purpose
                  ? <span className="field-error">{errors.purpose}</span>
                  : <span className="hint">
                      3 to 500 characters.{form.purpose.length > 0 && ` ${purposeLeft} left.`}
                    </span>}
              </label>
            </div>

            <div className="form-actions">
              <Button type="button" icon="shield" loading={busy} onClick={runCheck}>Check eligibility</Button>
              <Button type="submit" variant="primary" loading={busy}>Submit application</Button>
            </div>
          </form>
        </div>

        <div>
          {check && (
            <div className="card">
              <h2 style={{ marginTop: 0 }}>{check.eligible ? "Looks good" : "Not eligible as entered"}</h2>
              <dl className="kv">
                <dt>Estimated EMI</dt><dd className="num">{rupees(check.estimated_emi)} / month</dd>
                <dt>Room for EMIs</dt><dd className="num">{rupees(check.max_affordable_emi)} / month</dd>
              </dl>
              {check.problems.length > 0 && (
                <ul>
                  {check.problems.map((p, i) => <li key={i}>{p}</li>)}
                </ul>
              )}
              {(check.suggested_amount || check.suggested_tenure_months) && (
                <div className="chips" style={{ marginTop: "0.5rem" }}>
                  {check.suggested_amount && (
                    <Button size="sm" onClick={() => applySuggestion("amount_requested", Math.round(check.suggested_amount))}>
                      Use {rupees(check.suggested_amount)}
                    </Button>
                  )}
                  {check.suggested_tenure_months && (
                    <Button size="sm" onClick={() => applySuggestion("tenure_months", check.suggested_tenure_months)}>
                      Use {check.suggested_tenure_months} months
                    </Button>
                  )}
                </div>
              )}
              {!check.eligible && (
                <>
                  <div className="banner banner-warn" style={{ marginTop: "1rem", marginBottom: 0 }}>
                    <span>You can still submit, but it is likely to be rejected or sent back for more information.</span>
                  </div>
                  <Button variant="danger" style={{ marginTop: "0.75rem" }} loading={busy} onClick={() => submit(true)}>
                    Submit anyway
                  </Button>
                </>
              )}
            </div>
          )}
          {!check && (
            <div className="card">
              <h2 style={{ marginTop: 0 }}>Before you submit</h2>
              <p className="muted">
                Check eligibility to see the estimated EMI and whether the amount,
                tenure, income, credit score and age fit the bank's rules for this
                loan type.
              </p>
              <ul className="checklist">
                {["Tenure and amount for this loan type", "Income and CIBIL score",
                  "Employment and age", "Whether the EMI is affordable"].map((line) => (
                  <li key={line}><Icon name="check" size={14} className="muted" /><span>{line}</span></li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

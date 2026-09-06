// Staff create a borrower profile on a customer's behalf (the trainer's POST /applicants).

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, errorMessage } from "../api/client";
import ErrorBanner from "../components/ErrorBanner";
import Button from "../components/ui/Button";
import { EMPLOYMENT, checkCreditScore, checkDateOfBirth, checkEmail, checkIncome, checkName, checkPhone, collect } from "../utils/validation";
import { label, rupees } from "../utils/format";

const empty = {
  name: "", email: "", phone: "", annual_income: "", employment_status: "salaried",
  credit_score: "", date_of_birth: "", years_with_employer: "", existing_monthly_emi: "0",
};

export default function NewApplicant() {
  const navigate = useNavigate();
  const [form, setForm] = useState(empty);
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  async function handleSubmit(e) {
    e.preventDefault();
    const found = collect({
      name: checkName(form.name), email: checkEmail(form.email), phone: checkPhone(form.phone),
      annual_income: checkIncome(form.annual_income), credit_score: checkCreditScore(form.credit_score),
      date_of_birth: checkDateOfBirth(form.date_of_birth),
    });
    setErrors(found);
    if (Object.keys(found).length) return;
    setBusy(true);
    setError("");
    try {
      const res = await api.post("/applicants", {
        name: form.name.trim(), email: form.email.trim(), phone: form.phone.trim(),
        annual_income: Number(form.annual_income), employment_status: form.employment_status,
        credit_score: form.credit_score === "" ? null : Number(form.credit_score),
        date_of_birth: form.date_of_birth || null,
        years_with_employer: form.years_with_employer === "" ? null : Number(form.years_with_employer),
        existing_monthly_emi: Number(form.existing_monthly_emi || 0),
      });
      navigate("/applications/new", { state: { applicantId: res.data.id } });
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  const field = (name, text, props = {}, hint) => (
    <label>
      {text}
      <input value={form[name]} onChange={set(name)} {...props} />
      {errors[name] && <span className="field-error">{errors[name]}</span>}
      {hint && !errors[name] && <span className="hint">{hint}</span>}
    </label>
  );

  const income = Number(form.annual_income);

  return (
    <>
      <div className="page-head">
        <div>
          <h1>New borrower profile</h1>
          <p className="sub">
            The customer's record at the bank. Once it exists you can apply for a
            loan on their behalf.
          </p>
        </div>
      </div>
      <ErrorBanner message={error} onClose={() => setError("")} />

      <div className="card" style={{ maxWidth: 760 }}>
        <form onSubmit={handleSubmit} noValidate>
          <div className="form-section">
            <p className="form-section-title">Who they are</p>
            <div className="grid-2">
              {field("name", "Full name")}
              {field("email", "Email", { type: "email" })}
              {field("phone", "Mobile number", { inputMode: "numeric", maxLength: 10 }, "10 digits, starting 6 to 9")}
              {field("date_of_birth", "Date of birth", { type: "date" }, "Optional, but age is one of the lending rules")}
            </div>
          </div>

          <div className="form-section">
            <p className="form-section-title">What they earn and owe</p>
            <div className="grid-2">
              <label>
                Annual income (₹)
                <input value={form.annual_income} onChange={set("annual_income")} type="number" min={1} />
                {errors.annual_income
                  ? <span className="field-error">{errors.annual_income}</span>
                  : income > 0
                    ? <span className="amount-preview">{rupees(income)} a year</span>
                    : <span className="hint">Before tax, as declared.</span>}
              </label>
              <label>
                Employment
                <select value={form.employment_status} onChange={set("employment_status")}>
                  {EMPLOYMENT.map((v) => <option key={v} value={v}>{label(v)}</option>)}
                </select>
                <span className="hint">Unemployed applicants cannot be approved.</span>
              </label>
              {field("years_with_employer", "Years in current job", { type: "number", step: "0.5", min: 0 },
                     "Optional. Salaried need 6 months, self-employed 2 years.")}
              {field("existing_monthly_emi", "Existing monthly EMIs (₹)", { type: "number", min: 0 },
                     "Other loan payments they already make. Zero if none.")}
            </div>
          </div>

          <div className="form-section">
            <p className="form-section-title">Credit</p>
            <div className="grid-2">
              {field("credit_score", "CIBIL score", { type: "number", min: 300, max: 900 },
                     "Optional, 300 to 900. A personal loan needs one on file.")}
            </div>
          </div>

          <div className="form-actions">
            <Button type="submit" variant="primary" icon="check" loading={busy}>Create profile</Button>
            <Link className="btn btn-ghost" to="/applications/new">Cancel</Link>
          </div>
        </form>
      </div>
    </>
  );
}

// Customer signup. One form creates the login and the borrower profile (D-07, T-23).

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, errorMessage } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import ErrorBanner from "../components/ErrorBanner";
import Button from "../components/ui/Button";
import Icon from "../components/ui/Icon";
import {
  EMPLOYMENT, checkCreditScore, checkDateOfBirth, checkEmail, checkIncome, checkName,
  checkPassword, checkPhone, collect,
} from "../utils/validation";
import { label } from "../utils/format";

const empty = {
  name: "", email: "", password: "", phone: "",
  annual_income: "", employment_status: "salaried",
  credit_score: "", date_of_birth: "", years_with_employer: "", existing_monthly_emi: "0",
};

export default function ApplicantSignup() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(empty);
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  async function handleSubmit(e) {
    e.preventDefault();
    const found = collect({
      name: checkName(form.name),
      email: checkEmail(form.email),
      password: checkPassword(form.password),
      phone: checkPhone(form.phone),
      annual_income: checkIncome(form.annual_income),
      credit_score: checkCreditScore(form.credit_score),
      date_of_birth: checkDateOfBirth(form.date_of_birth),
      years_with_employer:
        form.years_with_employer !== "" && !(Number(form.years_with_employer) >= 0 && Number(form.years_with_employer) <= 60)
          ? "0 to 60 years" : "",
      existing_monthly_emi: Number(form.existing_monthly_emi) >= 0 ? "" : "Cannot be negative",
    });
    setErrors(found);
    if (Object.keys(found).length) return;

    // Blank optional fields are sent as nothing, not as empty strings.
    const payload = {
      name: form.name.trim(),
      email: form.email.trim(),
      password: form.password,
      phone: form.phone.trim(),
      annual_income: Number(form.annual_income),
      employment_status: form.employment_status,
      credit_score: form.credit_score === "" ? null : Number(form.credit_score),
      date_of_birth: form.date_of_birth || null,
      years_with_employer: form.years_with_employer === "" ? null : Number(form.years_with_employer),
      existing_monthly_emi: Number(form.existing_monthly_emi || 0),
    };

    setBusy(true);
    setError("");
    try {
      await api.post("/auth/register-applicant", payload);
      await login(payload.email, payload.password);
      navigate("/applications", { replace: true });
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  const field = (name, labelText, props = {}, hint) => (
    <label>
      {labelText}
      <input value={form[name]} onChange={set(name)} {...props} />
      {errors[name] && <span className="field-error">{errors[name]}</span>}
      {hint && !errors[name] && <span className="hint">{hint}</span>}
    </label>
  );

  return (
    <div className="auth-wrap">
    <div className="auth-card auth-card-wide">
      <div className="auth-brand">
        <span className="brand-mark"><Icon name="rupee" size={18} /></span>
        <strong>Loan Application Management</strong>
      </div>
      <h1>Create your account</h1>
      <p className="muted">Tell us about yourself once. Every application uses these details.</p>
      <ErrorBanner message={error} onClose={() => setError("")} />
      <form onSubmit={handleSubmit} noValidate>
        <div className="grid-2">
          {field("name", "Full name")}
          {field("email", "Email", { type: "email" })}
          {field("password", "Password", { type: "password" }, "8+ characters, one capital, one digit")}
          {field("phone", "Mobile number", { inputMode: "numeric", maxLength: 10 }, "10 digits, starts with 6 to 9")}
          {field("annual_income", "Annual income (₹)", { type: "number", min: 1 })}
          <label>
            Employment
            <select value={form.employment_status} onChange={set("employment_status")}>
              {EMPLOYMENT.map((v) => (
                <option key={v} value={v}>{label(v)}</option>
              ))}
            </select>
          </label>
          {field("credit_score", "CIBIL score (optional)", { type: "number", min: 300, max: 900 }, "300 to 900, if you have one")}
          {field("date_of_birth", "Date of birth (optional)", { type: "date" }, "Needed for the age rules")}
          {field("years_with_employer", "Years in current job (optional)", { type: "number", step: "0.5", min: 0 }, "0.5 means six months")}
          {field("existing_monthly_emi", "Existing monthly EMIs (₹)", { type: "number", min: 0 }, "Other loans you already pay")}
        </div>
        <Button type="submit" variant="primary" loading={busy}>
          {busy ? "Creating…" : "Create account"}
        </Button>
      </form>
      <div className="auth-foot">
        Already have an account? <Link to="/login">Sign in</Link>
      </div>
    </div>
    </div>
  );
}

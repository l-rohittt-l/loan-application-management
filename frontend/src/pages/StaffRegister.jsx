// Bank staff registration. This is the trainer's register address; it creates
// a loan officer. Managers are seeded, never self-registered (D-07).

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, errorMessage } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import ErrorBanner from "../components/ErrorBanner";
import { checkEmail, checkName, checkPassword, collect } from "../utils/validation";

export default function StaffRegister() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
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
    });
    setErrors(found);
    if (Object.keys(found).length) return;

    setBusy(true);
    setError("");
    try {
      await api.post("/auth/register", { ...form, email: form.email.trim() });
      await login(form.email.trim(), form.password);
      navigate("/applications", { replace: true });
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-card">
      <h1>Staff account</h1>
      <p className="muted">For loan officers. Manager accounts are created by the bank.</p>
      <ErrorBanner message={error} onClose={() => setError("")} />
      <form onSubmit={handleSubmit} noValidate>
        <label>
          Full name
          <input value={form.name} onChange={set("name")} />
          {errors.name && <span className="field-error">{errors.name}</span>}
        </label>
        <label>
          Work email
          <input type="email" value={form.email} onChange={set("email")} />
          {errors.email && <span className="field-error">{errors.email}</span>}
        </label>
        <label>
          Password
          <input type="password" value={form.password} onChange={set("password")} />
          {errors.password && <span className="field-error">{errors.password}</span>}
          <span className="hint">At least 8 characters, one capital letter, one digit.</span>
        </label>
        <button type="submit" className="btn btn-primary" disabled={busy}>
          {busy ? "Creating…" : "Create staff account"}
        </button>
      </form>
      <p className="muted">
        Already registered? <Link to="/login">Sign in</Link>
      </p>
    </div>
  );
}

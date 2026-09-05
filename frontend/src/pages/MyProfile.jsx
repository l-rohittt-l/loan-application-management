// The applicant's own borrower profile.

import { useEffect, useState } from "react";
import { api, errorMessage } from "../api/client";
import ErrorBanner from "../components/ErrorBanner";
import Spinner from "../components/Spinner";
import { formatDate, label, rupees } from "../utils/format";

export default function MyProfile() {
  const [me, setMe] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/applicants/me").then((r) => setMe(r.data)).catch((err) => setError(errorMessage(err)));
  }, []);

  if (error) return <ErrorBanner message={error} />;
  if (!me) return <Spinner />;

  return (
    <>
      <div className="page-head"><h1>My profile</h1></div>
      <div className="card" style={{ maxWidth: 640 }}>
        <dl className="kv">
          <dt>Name</dt><dd>{me.name}</dd>
          <dt>Email</dt><dd>{me.email}</dd>
          <dt>Phone</dt><dd>{me.phone}</dd>
          <dt>Employment</dt><dd>{label(me.employment_status)}</dd>
          <dt>Annual income</dt><dd>{rupees(me.annual_income)}</dd>
          <dt>CIBIL score</dt><dd>{me.credit_score ?? <span className="muted">not provided</span>}</dd>
          <dt>Date of birth</dt><dd>{me.date_of_birth ? formatDate(me.date_of_birth) : <span className="muted">not provided</span>}</dd>
          <dt>Years in current job</dt><dd>{me.years_with_employer ?? <span className="muted">not provided</span>}</dd>
          <dt>Existing monthly EMIs</dt><dd>{rupees(me.existing_monthly_emi)}</dd>
          <dt>Customer since</dt><dd>{formatDate(me.created_at)}</dd>
        </dl>
        <p className="hint" style={{ marginTop: "1rem" }}>
          Your details are stored on the bank's server and fetched with your login each time. Nothing is kept in this browser except your session.
        </p>
      </div>
    </>
  );
}

// The counts (user story 08), for staff.

import { useEffect, useState } from "react";
import { api, errorMessage } from "../api/client";
import ErrorBanner from "../components/ErrorBanner";
import Spinner from "../components/Spinner";
import StatusBadge from "../components/StatusBadge";
import { label, rupees } from "../utils/format";

function Bars({ data, badges }) {
  const max = Math.max(1, ...Object.values(data));
  return (
    <div className="bars">
      {Object.entries(data).map(([key, count]) => (
        <div className="bar-row" key={key}>
          <span>{badges ? <StatusBadge status={key} /> : label(key)}</span>
          <div className="bar"><span style={{ width: `${(count / max) * 100}%` }} /></div>
          <span className="num">{count}</span>
        </div>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  const load = () =>
    api.get("/dashboard/summary").then((r) => { setData(r.data); setError(""); }).catch((err) => setError(errorMessage(err)));

  useEffect(() => { load(); }, []);

  return (
    <>
      <div className="page-head">
        <h1>Dashboard</h1>
        <button type="button" className="btn btn-ghost" onClick={load}>Refresh</button>
      </div>
      <ErrorBanner message={error} onClose={() => setError("")} />
      {!data ? <Spinner /> : (
        <>
          <div className="tiles">
            <div className="tile"><div className="muted">Total applications</div><div className="big">{data.total_applications}</div></div>
            <div className="tile"><div className="muted">Awaiting review</div><div className="big">{data.pending_review}</div></div>
            <div className="tile"><div className="muted">Total requested</div><div className="big">{rupees(data.total_amount_requested)}</div></div>
            <div className="tile"><div className="muted">Approved, not yet paid</div><div className="big">{rupees(data.approved_amount)}</div></div>
          </div>
          <div className="detail-grid">
            <div className="card"><h2 style={{ marginTop: 0 }}>By status</h2><Bars data={data.by_status} badges /></div>
            <div className="card"><h2 style={{ marginTop: 0 }}>By loan type</h2><Bars data={data.by_loan_type} /></div>
          </div>
        </>
      )}
    </>
  );
}

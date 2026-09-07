// The manager's and officer's overview (user story 08).
//
// Why bars and not a pie chart:
// The trainer fixed five status colours we cannot change. Run through a colour
// accessibility check, those five are fine side by side as bars, but in a pie —
// where every colour sits against every other — purple and blue become
// indistinguishable to a viewer with red-green colour blindness, and red and
// orange are hard to tell apart even with normal colour vision. So: bars, with
// the status name written beside every one, so colour never has to carry the
// meaning on its own. See TRAPS-AND-DECISIONS T-38.
//
// The loan-type chart uses one single blue for every bar on purpose. There the
// length is the whole message; giving each type its own colour would suggest a
// meaning that is not there.

import { useCallback, useEffect, useState } from "react";
import { api, errorMessage } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import ErrorBanner from "../components/ErrorBanner";
import MorningBriefing from "../components/MorningBriefing";
import Spinner from "../components/Spinner";
import Button from "../components/ui/Button";
import EmptyState from "../components/ui/EmptyState";
import Icon from "../components/ui/Icon";
import { label, rupees } from "../utils/format";

// Workflow order, not alphabetical: this is the path an application travels.
const PIPELINE = ["submitted", "under_review", "approved", "rejected", "disbursed"];
const LOAN_TYPES = ["personal", "home", "auto"];
const ONE_BLUE = "#2a78d6";   // every loan-type bar, because length is the message

function percent(value, total) {
  if (!total) return 0;
  return Math.round((value / total) * 100);
}

/** One row: a written label, a bar, and the number. Never colour alone. */
function BarRow({ name, count, total, colour }) {
  const share = percent(count, total);
  return (
    <div className="bar-row" title={`${name}: ${count} of ${total} (${share}%)`}>
      <span className="bar-label">{name}</span>
      <div className="bar">
        <span style={{ width: `${total ? (count / total) * 100 : 0}%`, background: colour }} />
      </div>
      <span className="bar-value">
        {count}
        <small className="muted" style={{ fontWeight: 400, marginLeft: 4 }}>{share}%</small>
      </span>
    </div>
  );
}

export default function Dashboard() {
  const { isManager } = useAuth();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [justRefreshed, setJustRefreshed] = useState(false);

  const load = useCallback(async ({ isRefresh = false } = {}) => {
    if (isRefresh) setRefreshing(true);
    try {
      const res = await api.get("/dashboard/summary");
      setData(res.data);
      setError("");
      if (isRefresh) {
        // A brief tick, so pressing the button visibly did something.
        setJustRefreshed(true);
        setTimeout(() => setJustRefreshed(false), 1400);
      }
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  if (!data && !error) return <Spinner text="Loading the dashboard…" />;

  const total = data?.total_applications ?? 0;
  const busiestType = Math.max(1, ...LOAN_TYPES.map((t) => data?.by_loan_type?.[t] ?? 0));

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Dashboard</h1>
          <p className="sub">Every application in the branch, as it stands right now.</p>
        </div>
        <Button
          onClick={() => load({ isRefresh: true })}
          loading={refreshing}
          icon={justRefreshed ? "check" : "refresh"}
          className={justRefreshed ? "btn-ok" : ""}
        >
          {refreshing ? "Refreshing…" : justRefreshed ? "Up to date" : "Refresh"}
        </Button>
      </div>

      <ErrorBanner message={error} onClose={() => setError("")} />

      {/* The headline feature (D-13). Manager-only: it reads across every
          customer's file at once, which is a branch-level view. */}
      {isManager && <MorningBriefing />}

      {data && (
        <>
          {/* The four numbers worth knowing at a glance. */}
          <div className="tiles">
            <div className="tile">
              <div className="label">Total applications</div>
              <div className="big">{data.total_applications}</div>
            </div>
            <div className="tile">
              <div className="label">Awaiting review</div>
              <div className="big">{data.pending_review}</div>
              <div className="hint">Submitted or under review</div>
            </div>
            <div className="tile">
              <div className="label">Total requested</div>
              <div className="big">{rupees(data.total_amount_requested)}</div>
            </div>
            <div className="tile">
              <div className="label">Approved, not yet paid</div>
              <div className="big">{rupees(data.approved_amount)}</div>
            </div>
          </div>

          {total === 0 ? (
            <div className="card">
              <EmptyState icon="inbox" title="No applications yet">
                Once customers start applying, the pipeline and the totals will appear here.
              </EmptyState>
            </div>
          ) : (
            <div className="detail-grid">
              <div className="card">
                <div className="card-head">
                  <h2>Application pipeline</h2>
                  <span className="muted" style={{ fontSize: "0.82rem" }}>{total} in total</span>
                </div>

                {/* The whole pipeline as one bar, split into its parts. */}
                <div className="stack" role="img" aria-label="All applications, split by status">
                  {PIPELINE.filter((s) => (data.by_status[s] ?? 0) > 0).map((s) => (
                    <span
                      key={s}
                      style={{ flexGrow: data.by_status[s], background: `var(--status-${s})` }}
                      title={`${label(s)}: ${data.by_status[s]}`}
                    />
                  ))}
                </div>
                <div className="stack-key">
                  {PIPELINE.map((s) => (
                    <span key={s}>
                      <i style={{ background: `var(--status-${s})` }} />
                      {label(s)}
                    </span>
                  ))}
                </div>

                <hr className="divider" />

                {/* The same numbers as bars, each with its name written out. */}
                <div className="bars">
                  {PIPELINE.map((s) => (
                    <BarRow
                      key={s}
                      name={label(s)}
                      count={data.by_status[s] ?? 0}
                      total={total}
                      colour={`var(--status-${s})`}
                    />
                  ))}
                </div>
              </div>

              <div className="card">
                <div className="card-head">
                  <h2>By loan type</h2>
                </div>
                <div className="bars">
                  {LOAN_TYPES.map((t) => (
                    <div
                      className="bar-row"
                      key={t}
                      title={`${label(t)}: ${data.by_loan_type[t] ?? 0} of ${total}`}
                    >
                      <span className="bar-label">{label(t)}</span>
                      <div className="bar">
                        <span
                          style={{
                            width: `${((data.by_loan_type[t] ?? 0) / busiestType) * 100}%`,
                            background: ONE_BLUE,
                          }}
                        />
                      </div>
                      <span className="bar-value">{data.by_loan_type[t] ?? 0}</span>
                    </div>
                  ))}
                </div>
                <p className="hint" style={{ marginTop: "1rem" }}>
                  <Icon name="info" size={13} style={{ verticalAlign: "-2px", marginRight: 4 }} />
                  Bar length shows how many. One colour is used on purpose here — the
                  length is the message.
                </p>
              </div>
            </div>
          )}
        </>
      )}
    </>
  );
}

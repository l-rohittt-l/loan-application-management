// The stored details of one activity event, laid out as labelled rows rather
// than dumped as a line of JSON. Used by the Activity page and by the activity
// panel on an application.

import { DETAIL_LABELS, parseDetails } from "../utils/activity";
import { label, rupees } from "../utils/format";

function DetailValue({ name, value }) {
  if (value === null || value === undefined || value === "") return <span className="muted">not recorded</span>;
  if (typeof value === "boolean") return value ? <span className="tick">Yes</span> : <span className="cross">No</span>;
  if (name === "amount") return rupees(value);
  if (name === "tenure_months") return `${value} months`;
  if (name === "from" || name === "to") return label(value);
  if (name === "doc_type" || name === "loan_type") return label(value);
  return String(value);
}

export default function ActivityDetails({ raw }) {
  const parsed = parseDetails(raw);
  if (!parsed) return <p className="muted">Nothing further was recorded for this event.</p>;

  return (
    <dl className="kv">
      {Object.entries(parsed).map(([key, value]) => (
        <div key={key} style={{ display: "contents" }}>
          <dt>{DETAIL_LABELS[key] || label(key)}</dt>
          <dd><DetailValue name={key} value={value} /></dd>
        </div>
      ))}
    </dl>
  );
}

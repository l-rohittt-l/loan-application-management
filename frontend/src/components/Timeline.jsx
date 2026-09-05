// The vertical status history (user story 11). Oldest at the top, as the spec orders it.

import StatusBadge from "./StatusBadge";
import { formatDateTime } from "../utils/format";

export default function Timeline({ history = [] }) {
  if (!history.length) return <p className="muted">No status changes yet.</p>;
  return (
    <ol className="timeline">
      {history.map((h) => (
        <li key={h.id}>
          <div>
            {h.old_status ? (
              <>
                <StatusBadge status={h.old_status} /> <span className="muted">→</span>{" "}
              </>
            ) : null}
            <StatusBadge status={h.new_status} />
          </div>
          <div className="when">
            {formatDateTime(h.changed_at)} · {h.changed_by}
          </div>
          {h.remarks && <div className="remarks">{h.remarks}</div>}
        </li>
      ))}
    </ol>
  );
}

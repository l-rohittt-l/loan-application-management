// The five status colours, exactly as the trainer's user story 09 lists them:
// submitted = blue, under_review = orange, approved = green, rejected = red, disbursed = purple.

import { label } from "../utils/format";

export default function StatusBadge({ status }) {
  return <span className={`badge badge-${status}`}>{label(status)}</span>;
}

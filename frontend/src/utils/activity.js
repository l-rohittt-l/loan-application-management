// How an activity row is described in plain words.
//
// This lived inside the Activity page until the application detail page needed
// the same thing and was still printing raw stored data into a table cell. One
// copy, imported by both, so the two screens can never drift apart.

import { label } from "./format";

// Plain words and an icon for each kind of event, instead of the stored name.
export const ACTIONS = {
  staff_registered:      { text: "Staff account created",    icon: "user" },
  applicant_signed_up:   { text: "Customer signed up",       icon: "user" },
  login_succeeded:       { text: "Signed in",                icon: "shield" },
  login_failed:          { text: "Sign-in failed",           icon: "alert" },
  applicant_created:     { text: "Borrower profile created", icon: "user" },
  application_submitted: { text: "Application submitted",    icon: "file" },
  status_changed:        { text: "Status changed",           icon: "activity" },
  document_added:        { text: "Document added",           icon: "file" },
  document_verified:     { text: "Document verified",        icon: "check" },
  eligibility_checked:   { text: "Eligibility checked",      icon: "shield" },
  dashboard_viewed:      { text: "Dashboard viewed",         icon: "dashboard" },
};

export const describe = (action) => ACTIONS[action] || { text: label(action), icon: "info" };

// Turn a stored detail key into something readable.
export const DETAIL_LABELS = {
  from: "Changed from", to: "Changed to", remarks: "Remarks", reason: "Reason",
  loan_type: "Loan type", amount: "Amount", tenure_months: "Tenure",
  doc_type: "Document type", file_name: "File name", application_id: "Application",
  eligible: "Passed eligibility", problem_count: "Rules not met", email: "Email",
};

/** The stored details are a small piece of JSON. Hand back an object, or null. */
export function parseDetails(raw) {
  try {
    const parsed = raw ? JSON.parse(raw) : null;
    return parsed && Object.keys(parsed).length ? parsed : null;
  } catch {
    return null;
  }
}

/**
 * One line summarising what changed, for a table cell where a full list would
 * not fit. "Under review → Approved", "Aadhaar.pdf", and so on.
 */
export function summarise(action, raw) {
  const d = parseDetails(raw);
  if (!d) return "";
  if (action === "status_changed" && d.to) {
    return d.from ? `${label(d.from)} → ${label(d.to)}` : label(d.to);
  }
  if (action === "application_submitted" && d.loan_type) {
    return `${label(d.loan_type)} loan`;
  }
  if ((action === "document_added" || action === "document_verified") && d.doc_type) {
    return label(d.doc_type);
  }
  if (action === "eligibility_checked") {
    return d.eligible ? "Passed" : `${d.problem_count ?? 0} rule(s) not met`;
  }
  return "";
}

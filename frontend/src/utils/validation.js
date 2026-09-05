// Client-side checks that mirror the backend's rules (Rule 6).
//
// The server's check is the real one. These exist so the user sees a clear
// message before the round trip. Keep the numbers in step with
// backend/app/domain/rules.py.

export const LOAN_TYPES = ["personal", "home", "auto"];
export const EMPLOYMENT = ["salaried", "self_employed", "unemployed"];
export const DOCUMENT_TYPES = [
  "id_proof", "income_proof", "bank_statement", "property_docs", "employment_letter", "vehicle_quotation",
];

export const AMOUNT_MIN = 10_000;
export const AMOUNT_MAX = 10_000_000;
export const AMOUNT_LIMITS = { personal: 2_500_000, home: 10_000_000, auto: 5_000_000 };
export const TENURE_LIMITS = { personal: [12, 60], home: [12, 360], auto: [12, 84] };

const NAME = /^[A-Za-z][A-Za-z .'-]{1,99}$/;
const PHONE = /^[6-9]\d{9}$/;
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function checkName(v) {
  if (!v || !NAME.test(v.trim())) return "2 to 100 characters: letters, spaces, dots, apostrophes or hyphens";
  return "";
}
export function checkEmail(v) {
  if (!v || !EMAIL.test(v.trim())) return "Enter a valid email address";
  return "";
}
export function checkPhone(v) {
  if (!v || !PHONE.test(v.trim())) return "10-digit Indian mobile number starting with 6 to 9";
  return "";
}
export function checkPassword(v) {
  if (!v || v.length < 8 || v.length > 72) return "8 to 72 characters";
  if (!/[A-Z]/.test(v)) return "Needs at least one capital letter";
  if (!/\d/.test(v)) return "Needs at least one digit";
  return "";
}
export function checkCreditScore(v) {
  if (v === "" || v === null || v === undefined) return "";   // optional
  const n = Number(v);
  if (!Number.isInteger(n) || n < 300 || n > 900) return "CIBIL score is between 300 and 900";
  return "";
}
export function checkIncome(v) {
  const n = Number(v);
  if (!(n > 0)) return "Annual income must be more than zero";
  return "";
}
export function checkAmount(v, loanType) {
  const n = Number(v);
  if (!(n >= AMOUNT_MIN && n <= AMOUNT_MAX)) return `Between ₹10,000 and ₹1,00,00,000`;
  const cap = AMOUNT_LIMITS[loanType];
  if (cap && n > cap) return `A ${loanType} loan cannot exceed ₹${cap.toLocaleString("en-IN")}`;
  return "";
}
export function checkTenure(v, loanType) {
  const n = Number(v);
  const [lo, hi] = TENURE_LIMITS[loanType] || [6, 360];
  if (!Number.isInteger(n) || n < lo || n > hi) return `A ${loanType} loan runs ${lo} to ${hi} months`;
  return "";
}
export function checkPurpose(v) {
  const t = (v || "").trim();
  if (t.length < 3 || t.length > 500) return "3 to 500 characters";
  return "";
}
export function checkDateOfBirth(v) {
  if (!v) return "";   // optional
  const d = new Date(v);
  if (Number.isNaN(d.getTime())) return "Enter a valid date";
  if (d > new Date()) return "Cannot be in the future";
  if (d.getFullYear() < 1900) return "Not a plausible date";
  return "";
}
export function checkFileName(v) {
  const t = (v || "").trim().toLowerCase();
  if (!t || t.length > 255) return "1 to 255 characters";
  if (!/\.(pdf|jpe?g|png)$/.test(t)) return "Must end in .pdf, .jpg, .jpeg or .png";
  if (t.includes("/") || t.includes("\\")) return "No folder separators";
  return "";
}

// Run a set of checks and return {field: message} for the ones that failed.
export function collect(checks) {
  const errors = {};
  for (const [field, message] of Object.entries(checks)) {
    if (message) errors[field] = message;
  }
  return errors;
}

// Display helpers.

// Indian grouping: ₹25,00,000 not ₹2,500,000. The browser's built-in
// formatter knows the en-IN rules, so this is one line.
const inr = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});
export function rupees(amount) {
  if (amount === null || amount === undefined || amount === "") return "";
  return inr.format(Number(amount));
}

export function formatDate(value) {
  if (!value) return "";
  return new Date(value).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

export function formatDateTime(value) {
  if (!value) return "";
  return new Date(value).toLocaleString("en-IN", {
    day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

// "under_review" -> "Under review"
export function label(value) {
  if (!value) return "";
  const text = String(value).replace(/_/g, " ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

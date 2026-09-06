"""
The second front-end (user story 12), in Streamlit.

Run from the project root:
    backend\\venv\\Scripts\\streamlit run frontend-streamlit/app.py
Opens on http://localhost:8501. Talks to the same backend as the React app.

Streamlit turns this script into a web page. It re-runs the whole script on
every click, and `st.session_state` is the dictionary that survives between
runs. The login token lives there, on the server side of Streamlit, not in
the browser.
"""

import os
from datetime import date

import requests
import streamlit as st

# The backend address comes from the environment, same rule as React (D-12).
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/") + "/api/v1"

STATUSES = ["submitted", "under_review", "approved", "rejected", "disbursed"]
LOAN_TYPES = ["personal", "home", "auto"]
TENURE_LIMITS = {"personal": (12, 60), "home": (12, 360), "auto": (12, 84)}
# The trainer's exact colours (user story 09).
COLOURS = {"submitted": "#2563eb", "under_review": "#ea580c", "approved": "#16a34a",
           "rejected": "#dc2626", "disbursed": "#7c3aed"}

st.set_page_config(page_title="Loan Application Management", page_icon="₹", layout="wide")


# ---------------------------------------------------------------------------
# Talking to the backend
# ---------------------------------------------------------------------------

def _headers() -> dict:
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _error_text(response: requests.Response) -> str:
    try:
        detail = response.json().get("detail")
    except ValueError:
        return response.text or f"HTTP {response.status_code}"
    if isinstance(detail, list):
        return " · ".join(f"{e.get('loc', ['?'])[-1]}: {e.get('msg')}" for e in detail)
    return str(detail)


def api(method: str, path: str, **kwargs):
    """Call the backend. Returns (data, error_text). Never raises."""
    try:
        r = requests.request(method, f"{API_BASE}{path}", headers=_headers(), timeout=15, **kwargs)
    except requests.exceptions.ConnectionError:
        return None, "Cannot reach the backend. Is it running on port 8000?"
    if r.status_code == 401:
        st.session_state.pop("token", None)
        st.session_state.pop("user", None)
        return None, "Your session has ended. Please sign in again."
    if r.status_code >= 400:
        return None, _error_text(r)
    return (r.json() if r.content else {}), None


def rupees(n) -> str:
    """Indian grouping: ₹25,00,000."""
    n = int(round(float(n or 0)))
    s = str(abs(n))
    if len(s) <= 3:
        body = s
    else:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        body = ",".join(parts) + "," + tail
    return ("-" if n < 0 else "") + "₹" + body


def badge(status: str) -> str:
    colour = COLOURS.get(status, "#6b7280")
    text = status.replace("_", " ").capitalize()
    return (f'<span style="background:{colour};color:#fff;padding:2px 10px;border-radius:999px;'
            f'font-size:0.8rem;font-weight:600;white-space:nowrap">{text}</span>')


def label(v) -> str:
    return str(v or "").replace("_", " ").capitalize()


# ---------------------------------------------------------------------------
# Sidebar: sign in / sign out
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("₹ Loan Application Management")
    st.caption("Streamlit front-end · same backend as the React app")

    if "user" not in st.session_state:
        st.subheader("Sign in")
        with st.form("login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign in", use_container_width=True):
                data, err = api("POST", "/auth/login", json={"email": email.strip(), "password": password})
                if err:
                    st.error(err)
                else:
                    st.session_state["token"] = data["access_token"]
                    me, err = api("GET", "/auth/me")
                    if err:
                        st.error(err)
                    else:
                        st.session_state["user"] = me
                        st.rerun()
        st.info("Customers and bank staff sign in here. Accounts are created in the React app or by the seed script.")
    else:
        user = st.session_state["user"]
        st.markdown(f"**{user['name']}**  \n{label(user['role'])}")
        if st.button("Sign out", use_container_width=True):
            st.session_state.pop("token", None)
            st.session_state.pop("user", None)
            st.rerun()

if "user" not in st.session_state:
    st.title("Welcome")
    st.write("Sign in from the sidebar to see your applications.")
    st.stop()

user = st.session_state["user"]
is_staff = user["role"] in ("loan_officer", "branch_manager")
is_manager = user["role"] == "branch_manager"

tab_list, tab_new, tab_dash, tab_chat = st.tabs(
    ["Applications", "New application", "Dashboard", "Assistant"]
)

# ---------------------------------------------------------------------------
# Tab 1: the list, with filters and status colours, and one application's detail
# ---------------------------------------------------------------------------

with tab_list:
    st.subheader("My applications" if not is_staff else "Applications")
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    f_status = c1.selectbox("Status", ["All"] + STATUSES, format_func=label)
    f_type = c2.selectbox("Loan type", ["All"] + LOAN_TYPES, format_func=label)
    f_from = c3.date_input("Submitted from", value=None)
    f_to = c4.date_input("Submitted to", value=None)

    params = {"page": 1, "limit": 100}
    if f_status != "All":
        params["status"] = f_status
    if f_type != "All":
        params["loan_type"] = f_type
    if f_from:
        params["from_date"] = f_from.isoformat()
    if f_to:
        params["to_date"] = f_to.isoformat()

    data, err = api("GET", "/applications", params=params)
    if err:
        st.error(err)
    else:
        items = data["items"]
        st.caption(f"{data['total_count']} application(s)")
        if not items:
            st.info("No applications match.")
        else:
            rows = "".join(
                f"<tr><td>#{a['id']}</td><td>{a.get('applicant_name') or a['applicant_id']}</td>"
                f"<td>{label(a['loan_type'])}</td><td style='text-align:right'>{rupees(a['amount_requested'])}</td>"
                f"<td style='text-align:right'>{a['tenure_months']} mo</td><td>{badge(a['status'])}</td>"
                f"<td>{(a.get('submitted_at') or '')[:10]}</td></tr>"
                for a in items
            )
            st.markdown(
                "<table style='width:100%;border-collapse:collapse'>"
                "<thead><tr><th>ID</th><th>Applicant</th><th>Type</th><th style='text-align:right'>Amount</th>"
                "<th style='text-align:right'>Tenure</th><th>Status</th><th>Submitted</th></tr></thead>"
                f"<tbody>{rows}</tbody></table>",
                unsafe_allow_html=True,
            )

            st.divider()
            chosen = st.selectbox("Open an application", [a["id"] for a in items],
                                  format_func=lambda i: f"#{i}")
            detail, err = api("GET", f"/applications/{chosen}")
            docs, derr = api("GET", f"/applications/{chosen}/documents")
            if err:
                st.error(err)
            else:
                left, right = st.columns([2, 1])
                with left:
                    st.markdown(f"### Application #{detail['id']} &nbsp; {badge(detail['status'])}", unsafe_allow_html=True)
                    st.write(f"**{label(detail['loan_type'])} loan** · {rupees(detail['amount_requested'])} over "
                             f"{detail['tenure_months']} months")
                    st.write(f"Purpose: {detail['purpose']}")
                    if detail.get("applicant"):
                        a = detail["applicant"]
                        st.write(f"Applicant: **{a['name']}** · {a['email']} · {a['phone']} · "
                                 f"{label(a['employment_status'])} · income {rupees(a['annual_income'])} · "
                                 f"CIBIL {a['credit_score'] if a['credit_score'] is not None else 'not provided'}")
                    # Piece 19: the server's own assessment, taken at submission.
                    if detail.get("eligibility_summary"):
                        passed = detail.get("eligibility_passed")
                        with st.expander(f"Eligibility at submission — {'passed' if passed else 'did not pass'}"):
                            st.text(detail["eligibility_summary"])
                    st.markdown("**Documents**")
                    if not derr:
                        for t in docs["required"]:
                            have = any(d["doc_type"] == t for d in docs["items"])
                            st.write(("✅ " if have else "❌ ") + label(t))
                        for d in docs["items"]:
                            st.caption(f"{label(d['doc_type'])}: {d['file_name']} "
                                       f"({'verified' if d['verified'] else 'not verified'})")
                with right:
                    st.markdown("**Status history**")
                    for h in detail["status_history"]:
                        arrow = f"{label(h['old_status'])} → " if h.get("old_status") else ""
                        st.write(f"{arrow}**{label(h['new_status'])}**  \n"
                                 f"<small>{(h.get('changed_at') or '')[:16].replace('T', ' ')} · {h['changed_by']}</small>",
                                 unsafe_allow_html=True)
                        if h.get("remarks"):
                            st.caption(h["remarks"])

                    if is_staff:
                        nxt = {"submitted": ["under_review"], "under_review": ["approved", "rejected"],
                               "approved": ["disbursed"]}.get(detail["status"], [])
                        if not is_manager:
                            nxt = [s for s in nxt if s != "disbursed"]
                        if nxt:
                            st.markdown("**Update status**")
                            with st.form(f"status_{chosen}"):
                                new_status = st.selectbox("Move to", nxt, format_func=label)
                                remarks = st.text_area("Remarks", max_chars=1000)
                                if st.form_submit_button("Update"):
                                    _, uerr = api("PATCH", f"/applications/{chosen}/status",
                                                  json={"new_status": new_status, "remarks": remarks or None})
                                    if uerr:
                                        st.error(uerr)
                                    else:
                                        st.success(f"Moved to {label(new_status)}.")
                                        st.rerun()
                        elif detail["status"] == "approved":
                            st.caption("Only a branch manager can disburse this loan.")

# ---------------------------------------------------------------------------
# Tab 2: the form, with the eligibility check
# ---------------------------------------------------------------------------

with tab_new:
    st.subheader("Apply for a loan" if not is_staff else "New application")

    if is_staff:
        applicants, err = api("GET", "/applicants", params={"limit": 100})
        if err:
            st.error(err)
            applicant_id = None
        else:
            options = {f"{a['name']} · {a['email']}": a["id"] for a in applicants["items"]}
            pick = st.selectbox("Applicant", list(options) or ["No applicants yet"])
            applicant_id = options.get(pick)
    else:
        me, err = api("GET", "/applicants/me")
        applicant_id = me["id"] if not err else None
        if err:
            st.error(err)
        else:
            st.caption(f"Applying as {me['name']} ({me['email']})")

    loan_type = st.selectbox("Loan type", LOAN_TYPES, format_func=label)
    lo, hi = TENURE_LIMITS[loan_type]
    amount = st.number_input("Amount (₹)", min_value=10_000, max_value=10_000_000, value=500_000, step=10_000)
    tenure = st.number_input("Tenure (months)", min_value=lo, max_value=hi, value=lo, step=6,
                             help=f"{label(loan_type)} loans run {lo} to {hi} months")
    purpose = st.text_area("Purpose", max_chars=500)

    col_a, col_b = st.columns(2)
    if col_a.button("Check eligibility", use_container_width=True, disabled=applicant_id is None):
        result, err = api("POST", "/applications/check-eligibility",
                          json={"applicant_id": applicant_id, "loan_type": loan_type,
                                "amount_requested": amount, "tenure_months": int(tenure)})
        if err:
            st.error(err)
        else:
            st.session_state["last_check"] = result
    if col_b.button("Submit application", type="primary", use_container_width=True, disabled=applicant_id is None):
        if len(purpose.strip()) < 3:
            st.error("Purpose needs at least 3 characters.")
        else:
            created, err = api("POST", "/applications",
                               json={"applicant_id": applicant_id, "loan_type": loan_type,
                                     "amount_requested": amount, "tenure_months": int(tenure),
                                     "purpose": purpose.strip()})
            if err:
                st.error(err)
            else:
                st.success(f"Application #{created['id']} submitted.")
                st.session_state.pop("last_check", None)

    if "last_check" in st.session_state:
        r = st.session_state["last_check"]
        (st.success if r["eligible"] else st.warning)("Looks eligible" if r["eligible"] else "Not eligible as entered")
        st.write(f"Estimated EMI **{rupees(r['estimated_emi'])}** a month · room for EMIs **{rupees(r['max_affordable_emi'])}**")
        # Piece 19: every rule, passed or failed — not only the failures.
        for row in r.get("rule_checks", []):
            st.write(("✅ " if row["passed"] else "❌ ") + row["label"])
        if r.get("suggested_amount"):
            st.caption(f"Suggested amount: {rupees(r['suggested_amount'])}")
        if r.get("suggested_tenure_months"):
            st.caption(f"Suggested tenure: {r['suggested_tenure_months']} months")

# ---------------------------------------------------------------------------
# Tab 3: the dashboard
# ---------------------------------------------------------------------------

with tab_dash:
    st.subheader("Dashboard")
    if not is_staff:
        st.info("The dashboard is for bank staff.")
    else:
        d, err = api("GET", "/dashboard/summary")
        if err:
            st.error(err)
        else:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total applications", d["total_applications"])
            m2.metric("Awaiting review", d["pending_review"])
            m3.metric("Total requested", rupees(d["total_amount_requested"]))
            m4.metric("Approved, not yet paid", rupees(d["approved_amount"]))
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**By status**")
                st.bar_chart({label(k): v for k, v in d["by_status"].items()})
            with c2:
                st.markdown("**By loan type**")
                st.bar_chart({label(k): v for k, v in d["by_loan_type"].items()})


# ---------------------------------------------------------------------------
# Tab 4: the assistant (Phase 2)
# ---------------------------------------------------------------------------
# Talks to the same POST /api/v1/chat address the React page uses, so both
# front-ends get whatever brain sits behind that door — the RAG chain today,
# the tool-using agent from Phase 3 onwards. Nothing here needs changing when
# that swap happens.
#
# Every answer shows the manual extracts it came from, exactly as the React
# page does. An assistant that cites its source can be checked; one that does
# not has to be trusted, and for a bank that difference matters.

# What each brain is called on screen. Mirrors MODES in the React Assistant page.
CHAT_MODES = {
    "rag": "Answered from the user manual",
    "agent": "Read live application data",
    "review": "Multi-agent review",
    "empty": "",
}

SUGGESTED_QUESTIONS = [
    "What documents are required for a home loan?",
    "What is the minimum CIBIL score for a personal loan?",
    "What happens if my application is rejected?",
]

with tab_chat:
    st.subheader("Assistant")
    st.caption(
        "Ask about loan policy, eligibility, documents or fees. Every answer "
        "comes from the bank's user manual, and shows you where it came from."
    )

    st.session_state.setdefault("chat_log", [])

    # The conversation so far, oldest first.
    for entry in st.session_state["chat_log"]:
        st.markdown(f"**You:** {entry['question']}")
        st.markdown(entry["answer"])
        mode_text = CHAT_MODES.get(entry["mode"], entry["mode"])
        st.caption(f"{mode_text} · {entry['ms'] / 1000:.1f}s")
        sources = entry.get("sources") or []
        if sources:
            plural = "" if len(sources) == 1 else "s"
            with st.expander(f"Show the {len(sources)} manual extract{plural} this came from"):
                for source in sources:
                    st.code(source.get("chunk_id") or "chunk", language=None)
                    st.text(source.get("excerpt", ""))
        st.divider()

    if not st.session_state["chat_log"]:
        st.info(
            "I answer only from the bank's user manual. If something is not in "
            "there, I will say so rather than guess."
        )
        st.markdown("**Try asking:**")
        for question in SUGGESTED_QUESTIONS:
            st.markdown(f"- {question}")

    with st.form("chat_form", clear_on_submit=True):
        question = st.text_input("Your question", placeholder="e.g. How long does approval take?")
        asked = st.form_submit_button("Ask")

    if asked and question.strip():
        with st.spinner("Thinking…"):
            answer, err = api("POST", "/chat", json={"message": question.strip()})
        if err:
            st.error(err)
        else:
            st.session_state["chat_log"].append({
                "question": question.strip(),
                "answer": answer.get("answer", ""),
                "mode": answer.get("mode", "rag"),
                "sources": answer.get("sources", []),
                "ms": answer.get("duration_ms", 0.0),
            })
            st.rerun()

    if st.session_state["chat_log"]:
        if st.button("Clear conversation"):
            st.session_state["chat_log"] = []
            st.rerun()

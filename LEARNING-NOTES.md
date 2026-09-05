# Learning notes

Things worth knowing that came up while building. Written to be read again later. Short on purpose.

---

## How much of your salary can go to loan EMIs — the FOIR rule

**FOIR** stands for Fixed Obligation to Income Ratio. It is the share of your monthly income that already goes to fixed payments, including the new loan you are asking for. Banks use it to decide if you can afford one more EMI.

**The general rule in India:** all your EMIs together should stay under **50% of your monthly income.** Some banks use gross income, some use take-home pay.

**By loan type, in 2026:**

| Loan | What banks typically allow |
|---|---|
| Home loan | 40% to 55% of monthly income. Some lenders go to 60–65% for high earners. |
| Personal loan | 50% to 55%. A few stop at 45%. Some go to 60% for very high earners. |
| Car loan | Follows the same principle as the others. |

**Banks often step it up by income:**

| Monthly income | Usual cap |
|---|---|
| Up to ₹50,000 | 50% |
| ₹50,000 to ₹1,00,000 | 55% |
| Above ₹1,00,000 | 60% to 65%, depending on the lender |

The reasoning: someone earning ₹3 lakh a month can give up 60% and still live comfortably. Someone earning ₹30,000 cannot.

**What we use in the app:** 50% for all three loan types. One number, matches the manual, easy to explain.

Sources: [eligibilitytools.in](https://eligibilitytools.in/guides/home-loan-eligibility-india/), [GoCredit FOIR guide](https://gocredit.money/blog/foir-ratio-for-personal-loan), [Ruloans 2026 eligibility](https://www.ruloans.com/blog/home-loan-eligibility-india-2026/)

---

## Indian number grouping, and why software gets it wrong

Most programming languages group digits in threes: 2,500,000. India groups the last three digits, then twos: 25,00,000. Same number, and to an Indian reader the first one looks like a typo.

The names follow the groups. 1,00,000 is one lakh. 1,00,00,000 is one crore. So ₹25,00,000 reads instantly as "twenty-five lakh", while ₹2,500,000 makes you count.

Python, JavaScript and most libraries default to the Western style. Any app for an Indian bank needs its own formatter. Ours is `format_rupees` in `backend/app/utils/finance.py`, and it is used everywhere a rupee amount is shown in a message.

---

## Why banks never show customers their internal risk score

When a bank scores your application, that score and the rules behind it stay inside the bank. Customers see the outcome, not the working.

Two reasons. First, if customers knew the exact rules, some would arrange their paperwork to just clear each line, which defeats the point. Second, the scoring model is the bank's competitive edge, so it is treated like a trade secret.

This is why "aim it at managers" was Koushik's feedback on the risk tool. Staff see the score. Applicants see approve, reject, or "we need more documents".

"""
Loan maths.

`calculate_emi(principal, annual_rate, tenure_months)` is called by that
exact name and path in the trainer's UNIT-03 test, which expects about
16,607 for 500000 at 12% over 36 months.

EMI stands for Equated Monthly Installment: the fixed amount paid every
month. The formula is the standard one from manual Section 7:

    EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)

    P = the loan amount
    r = the monthly interest rate = annual rate / 12 / 100
    n = the number of months
"""

from app.domain import rules


def format_rupees(amount: float) -> str:
    """
    Indian digit grouping: the last three digits, then groups of two.
    2500000 -> ₹25,00,000   (twenty-five lakh)
    16607   -> ₹16,607
    Python's default `f"{n:,}"` would give ₹2,500,000, which reads wrong here.
    """
    n = int(round(amount))
    sign = "-" if n < 0 else ""
    digits = str(abs(n))
    if len(digits) <= 3:
        return f"{sign}₹{digits}"
    head, tail = digits[:-3], digits[-3:]
    groups: list[str] = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return f"{sign}₹{','.join(groups)},{tail}"


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """The fixed monthly payment, in rupees, rounded to 2 decimals."""
    if principal <= 0 or tenure_months <= 0:
        raise ValueError("principal and tenure_months must be positive")
    if annual_rate <= 0:
        # Interest-free: just spread the principal evenly.
        return round(principal / tenure_months, 2)

    r = annual_rate / 12 / 100
    growth = (1 + r) ** tenure_months
    emi = principal * r * growth / (growth - 1)
    return round(emi, 2)


def max_principal_for_emi(emi: float, annual_rate: float, tenure_months: int) -> float:
    """
    The largest loan whose EMI would be `emi`. The EMI formula run backwards.
    Used to suggest an affordable amount.
    """
    if emi <= 0 or tenure_months <= 0:
        return 0.0
    if annual_rate <= 0:
        return round(emi * tenure_months, 2)

    r = annual_rate / 12 / 100
    growth = (1 + r) ** tenure_months
    principal = emi * (growth - 1) / (r * growth)
    return round(principal, 2)


def max_affordable_emi(annual_income: float, existing_monthly_emi: float = 0.0) -> float:
    """
    How much EMI this person can take on: the allowed share of monthly
    income (50%, D-14) minus what they already pay to other loans.
    """
    monthly_income = annual_income / 12
    room = monthly_income * rules.EMI_MAX_SHARE_OF_INCOME - (existing_monthly_emi or 0.0)
    return round(max(room, 0.0), 2)

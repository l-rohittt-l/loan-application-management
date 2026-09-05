"""
"Would this loan be allowed?" — asked by the form before submitting (D-01).

Advisory only. It never blocks a submission; it explains problems and
suggests a fix where it can. Every threshold comes from the rules file.
"""

import structlog
from sqlalchemy.orm import Session

from app.domain import rules
from app.models.applicant import Applicant, EmploymentStatus
from app.models.user import User, UserRole
from app.schemas.application import EligibilityCheckRequest, EligibilityCheckResponse
from app.services import activity_service
from app.services.errors import Forbidden, NotFound
from app.utils.dates import age_on
from app.utils.finance import (
    calculate_emi, format_rupees, max_affordable_emi, max_principal_for_emi,
)

logger = structlog.get_logger()

_rupees = format_rupees   # Indian grouping: ₹25,00,000 not ₹2,500,000


def check(
    db: Session, data: EligibilityCheckRequest, *, viewer: User, meta: dict | None = None
) -> EligibilityCheckResponse:
    applicant = db.query(Applicant).filter(Applicant.id == data.applicant_id).first()
    if applicant is None:
        raise NotFound("Applicant not found")
    if viewer.role == UserRole.applicant and applicant.user_id != viewer.id:
        raise Forbidden("You can only check eligibility for yourself")

    loan_type = data.loan_type.value
    amount = data.amount_requested
    tenure = data.tenure_months
    problems: list[str] = []
    suggested_amount: float | None = None
    suggested_tenure: int | None = None

    # ---- Tenure and amount, per loan type (D-02, D-03) ----
    lo, hi = rules.tenure_range(loan_type)
    if not lo <= tenure <= hi:
        problems.append(f"A {loan_type} loan must run between {lo} and {hi} months.")
        suggested_tenure = min(max(tenure, lo), hi)
    cap = rules.amount_limit(loan_type)
    if amount > cap:
        problems.append(f"A {loan_type} loan cannot exceed {_rupees(cap)}.")
        suggested_amount = float(cap)

    # ---- Income (manual Section 5) ----
    min_income = rules.MIN_ANNUAL_INCOME[loan_type]
    if applicant.annual_income < min_income:
        problems.append(
            f"A {loan_type} loan needs an annual income of at least {_rupees(min_income)}; "
            f"the profile shows {_rupees(applicant.annual_income)}."
        )

    # ---- Credit score (manual Section 5 and FAQ) ----
    min_cibil = rules.MIN_CIBIL_SCORE[loan_type]
    if applicant.credit_score is None:
        if loan_type == "personal":
            problems.append(
                "Personal loans need a CIBIL score. Applicants without one may be "
                "considered for a home or auto loan instead."
            )
    elif applicant.credit_score < min_cibil:
        problems.append(
            f"A {loan_type} loan needs a CIBIL score of at least {min_cibil}; "
            f"the profile shows {applicant.credit_score}."
        )

    # ---- Employment (manual Section 5 and FAQ, D-16) ----
    if applicant.employment_status == EmploymentStatus.unemployed:
        problems.append("Applicants must be salaried or self-employed.")
    else:
        need = rules.MIN_YEARS_WITH_EMPLOYER.get(applicant.employment_status.value)
        have = applicant.years_with_employer
        if need is not None and have is not None and have < need:
            months = int(round(need * 12))
            what = "with the current employer" if applicant.employment_status == EmploymentStatus.salaried else "of business history"
            problems.append(f"Needs at least {months} months {what}; the profile shows {have:g} years.")

    # ---- Age (manual Section 5, D-05) ----
    if applicant.date_of_birth is not None:
        age = age_on(applicant.date_of_birth)
        min_age, max_age = rules.AGE_LIMITS[loan_type]
        if not min_age <= age <= max_age:
            problems.append(f"A {loan_type} loan is available from age {min_age} to {max_age}; the applicant is {age}.")
        elif loan_type == "home":
            # The loan must be fully repaid before 70.
            months_left = (rules.HOME_LOAN_MUST_END_BEFORE_AGE - age) * 12
            if tenure > months_left:
                problems.append(
                    f"A home loan must be repaid before age {rules.HOME_LOAN_MUST_END_BEFORE_AGE}. "
                    f"At {age}, the longest tenure is {months_left} months."
                )
                suggested_tenure = min(months_left, hi) if months_left >= lo else None

    # ---- Affordability (D-14): this EMI plus existing EMIs within 50% of income ----
    rate = rules.DEFAULT_ANNUAL_INTEREST_RATE
    estimated_emi = calculate_emi(amount, rate, tenure)
    affordable = max_affordable_emi(applicant.annual_income, applicant.existing_monthly_emi)
    if estimated_emi > affordable:
        share = int(rules.EMI_MAX_SHARE_OF_INCOME * 100)
        problems.append(
            f"The estimated EMI of {_rupees(estimated_emi)} a month is more than the {share}% of "
            f"monthly income available for loan payments ({_rupees(affordable)})."
        )
        if suggested_amount is None:
            ok_amount = max_principal_for_emi(affordable, rate, tenure)
            if ok_amount >= rules.AMOUNT_MIN:
                suggested_amount = round(ok_amount, -3)   # to the nearest thousand
        if suggested_tenure is None:
            # The shortest tenure in range at which this amount becomes affordable.
            for months in range(lo, hi + 1, 6):
                if calculate_emi(amount, rate, months) <= affordable:
                    suggested_tenure = months
                    break

    result = EligibilityCheckResponse(
        eligible=not problems,
        problems=problems,
        estimated_emi=estimated_emi,
        max_affordable_emi=affordable,
        suggested_amount=suggested_amount,
        suggested_tenure_months=suggested_tenure,
    )

    activity_service.record(
        db, action="eligibility_checked",
        actor_id=viewer.email, actor_role=viewer.role.value,
        entity_type="applicant", entity_id=applicant.id,
        details={"loan_type": loan_type, "amount": amount, "tenure_months": tenure,
                 "eligible": result.eligible, "problem_count": len(problems)},
        **(meta or {}),
    )
    db.commit()
    logger.info("eligibility_checked", applicant_id=applicant.id, loan_type=loan_type,
                eligible=result.eligible, problems=len(problems))
    return result

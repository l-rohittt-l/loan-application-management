"""
Small checks shared by several schemas, so each rule is written once.
"""

import re
from datetime import date

# Letters, spaces, dots, apostrophes and hyphens. Covers "Priya Sharma",
# "A.C. Harish", "O'Brien". Must start with a letter.
_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z .'\-]{1,99}$")

# Indian mobile: ten digits, first digit 6 to 9.
_PHONE_PATTERN = re.compile(r"^[6-9]\d{9}$")


def check_name(value: str) -> str:
    value = value.strip()
    if not _NAME_PATTERN.match(value):
        raise ValueError(
            "name must be 2 to 100 characters: letters, spaces, dots, apostrophes or hyphens"
        )
    return value


def check_phone(value: str) -> str:
    value = value.strip()
    if not _PHONE_PATTERN.match(value):
        raise ValueError("phone must be a 10-digit Indian mobile number starting with 6 to 9")
    return value


def check_password(value: str) -> str:
    # 72 is bcrypt's hard limit; anything longer is silently cut, which is worse
    # than refusing it.
    if not 8 <= len(value) <= 72:
        raise ValueError("password must be 8 to 72 characters")
    if not any(c.isupper() for c in value):
        raise ValueError("password must contain at least one uppercase letter")
    if not any(c.isdigit() for c in value):
        raise ValueError("password must contain at least one digit")
    return value


def check_date_of_birth(value: date | None) -> date | None:
    if value is None:
        return None
    today = date.today()
    if value > today:
        raise ValueError("date_of_birth cannot be in the future")
    if value.year < 1900:
        raise ValueError("date_of_birth is not plausible")
    return value

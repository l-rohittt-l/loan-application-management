"""
Date helpers.
"""

from datetime import date


def age_on(date_of_birth: date, on: date | None = None) -> int:
    """
    Whole years between a date of birth and a day (today by default).
    Handles the birthday-not-yet-reached case correctly.
    """
    on = on or date.today()
    years = on.year - date_of_birth.year
    if (on.month, on.day) < (date_of_birth.month, date_of_birth.day):
        years -= 1
    return years

"""
Form validation helpers.

Each function checks ONE thing and returns an error message as text,
or None when the value is fine. `validate_profile()` runs all the checks
and gives back a list of error messages.

These are plain Python functions (no Streamlit inside), so they can be
reused later by a FastAPI backend or tested on their own.
"""

from __future__ import annotations

# The words we use in the form for "no choice made".
ANY_PROVINCE = "Any province"
NOT_SURE = "Not sure yet"

# A sensible upper limit so a typing mistake is caught early.
MAX_BUDGET_USD = 100_000


def check_name(name: str):
    """First name is optional. If it is given, keep it short and letters only."""
    name = (name or "").strip()
    if not name:
        return None  # empty is allowed
    if len(name) > 40:
        return "Your name is too long. Please use 40 characters or fewer."
    # Allow letters, spaces, hyphens and apostrophes (for names like Sok-Dara).
    if not all(c.isalpha() or c in " -'" for c in name):
        return "Please use letters only in your name."
    return None


def check_budget(budget, no_budget_limit: bool):
    """
    Budget must be a positive number in USD, unless the student ticked
    "No budget limit".
    """
    if no_budget_limit:
        return None  # nothing to check

    if budget is None:
        return "Please enter your yearly budget in USD, or tick 'No budget limit'."

    try:
        budget = float(budget)
    except (TypeError, ValueError):
        return "Your budget must be a number, for example 1200."

    if budget <= 0:
        return "Your budget must be greater than 0 USD. Tick 'No budget limit' if you do not have one."
    if budget > MAX_BUDGET_USD:
        return f"That budget looks too high. Please enter a number up to {MAX_BUDGET_USD:,} USD."
    return None


def check_university_type(uni_type: str):
    """Type must be one of the three choices we offer."""
    if uni_type not in ("Public", "Private", "Either"):
        return "Please choose Public, Private or Either."
    return None


def validate_profile(profile: dict) -> list:
    """
    Check a whole profile dictionary from the home page form.

    Returns a list of error messages. An empty list means the form is valid.
    Note: "Not sure yet" for the major is allowed on purpose - we then rank
    using province, budget and type only.
    """
    errors = []

    for error in (
        check_name(profile.get("name", "")),
        check_budget(profile.get("budget"), profile.get("no_budget_limit", False)),
        check_university_type(profile.get("uni_type", "Either")),
    ):
        if error:
            errors.append(error)

    return errors


def describe_profile(profile: dict) -> str:
    """Turn a saved profile into one friendly sentence, used on the Results page."""
    major = profile.get("major", NOT_SURE)
    province = profile.get("province", ANY_PROVINCE)
    uni_type = profile.get("uni_type", "Either")

    parts = []
    parts.append("any major" if major == NOT_SURE else f"**{major}**")
    parts.append("in any province" if province == ANY_PROVINCE else f"in **{province}**")

    if profile.get("no_budget_limit"):
        parts.append("with no budget limit")
    else:
        parts.append(f"with a budget of **${float(profile.get('budget') or 0):,.0f}/year**")

    parts.append("at any type of university" if uni_type == "Either" else f"at a **{uni_type}** university")

    return ", ".join(parts)

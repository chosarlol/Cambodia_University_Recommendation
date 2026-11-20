"""
The recommendation form.

It lives in its own file because two pages use exactly the same form:
  - the Home page (as the "quick form"),
  - the "Find My University" page (as the main form).

Keeping it here means there is only one copy to explain and to fix.
"""

import streamlit as st

from services import data
from utils import state, validation
from utils.validation import ANY_PROVINCE, NOT_SURE


def safe_index(options: list, value, fallback: int = 0) -> int:
    """
    Find where `value` sits in `options` so a dropdown can be pre-filled.
    Returns `fallback` when the value is not in the list.
    """
    try:
        return options.index(value)
    except (ValueError, AttributeError):
        return fallback


def render_welcome_back(profile: dict):
    """Greet a visitor who has already filled in the form once."""
    greeting = f"Welcome back, {profile['name']}!" if profile.get("name") else "Welcome back!"
    st.success(
        f"**{greeting}** We kept your answers, so you only need to change "
        "what is different this time."
    )


def render_recommendation_form(form_key: str = "recommendation_form"):
    """
    Draw the form, check the answers, and open the Results page on success.

    The fields are built from the data, never from a hardcoded list.
    """
    profile = state.get_profile()

    major_options = [NOT_SURE] + data.list_majors()
    province_options = [ANY_PROVINCE] + data.list_provinces()
    type_options = ["Public", "Private", "Either"]

    with st.form(form_key):
        row1_left, row1_right = st.columns(2)

        with row1_left:
            major = st.selectbox(
                "Preferred major or field",
                options=major_options,
                index=safe_index(major_options, profile.get("major"), 0),
                help="Start typing to search. Choose 'Not sure yet' to skip this.",
            )

        with row1_right:
            province = st.selectbox(
                "Preferred province",
                options=province_options,
                index=safe_index(province_options, profile.get("province"), 0),
            )

        row2_left, row2_right = st.columns(2)

        with row2_left:
            budget = st.number_input(
                "Yearly budget (USD)",
                min_value=0,
                max_value=validation.MAX_BUDGET_USD,
                value=int(profile.get("budget") or 1000),
                step=50,
                help="How much you can pay for one year of study.",
            )
            no_budget_limit = st.checkbox(
                "No budget limit",
                value=bool(profile.get("no_budget_limit", False)),
            )

        with row2_right:
            uni_type = st.radio(
                "University type",
                options=type_options,
                index=safe_index(type_options, profile.get("uni_type"), 2),
                horizontal=True,
            )
            name = st.text_input(
                "Your first name (optional)",
                value=profile.get("name", ""),
                placeholder="So we can greet you",
                max_chars=40,
            )

        submitted = st.form_submit_button(
            "Get my recommendations →", type="primary", width="stretch"
        )

    # Everything below runs only after the button is pressed.
    if submitted:
        new_profile = {
            "name": name.strip(),
            "major": major,
            "province": province,
            # None means "no limit", so the ranking code knows not to filter.
            "budget": None if no_budget_limit else float(budget),
            "no_budget_limit": no_budget_limit,
            "uni_type": uni_type,
        }

        errors = validation.validate_profile(new_profile)

        if errors:
            # Show every problem at once so the student can fix them together.
            for error in errors:
                st.error(error)
        else:
            state.save_profile(new_profile)
            st.session_state["show_form_hint"] = False
            st.switch_page("pages/results.py")

    # "Clear my answers" must sit OUTSIDE the form, because a Streamlit form
    # can only contain its own submit button.
    if profile:
        if st.button("Clear my answers", key=f"clear_{form_key}"):
            state.clear_profile()
            st.rerun()

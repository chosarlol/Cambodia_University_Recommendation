"""
University Detail page.

Shows everything we know about ONE university: address, contact, website,
majors, fees and where the data came from.

The visitor arrives here by clicking a university name on the Explore,
Results or Favorites page. The id is kept in st.session_state and also in
the web address (?uni=...), so the link can be refreshed or shared.

Rule: when a fee is not in our data we print "Fee not published".
We never guess a number.
"""

import pandas as pd
import streamlit as st

from services import data
from utils import state, style


def split_values(text: str) -> list:
    """
    The source file puts several phone numbers or emails in one cell,
    separated by ';'. This turns that into a clean list.
    """
    if not text:
        return []
    return [part.strip() for part in text.split(";") if part.strip()]


def render_empty_state():
    """Shown when nobody has picked a university yet."""
    st.title("🏫 University details")
    st.info("No university selected yet.")
    st.write("Pick a university from the Explore page to see its full details.")
    if st.button("Go to Explore", type="primary"):
        st.switch_page("pages/browse.py")


def render_header(university: dict):
    """University name, Khmer name, and the type/province line."""
    st.title(university["name"])

    # Only show a Khmer name when the data really has one.
    if university.get("name_kh"):
        st.subheader(university["name_kh"])

    founded = university["established_year"] or "year not published"
    st.caption(f"{university['type']} university · {university['province']} · founded {founded}")

    # A clear warning when this is one of our invented test rows.
    if university["is_sample"]:
        st.error(
            "**This is SAMPLE data, not a real university.** It exists only to "
            "test the website. Its fees, website and contact details are invented."
        )


def render_actions(university: dict):
    """The buttons: official website, favorite, compare."""
    uni_id = university["id"]
    col1, col2, col3 = st.columns(3)

    # --- Official website -------------------------------------------------
    with col1:
        websites = split_values(university["website"])
        if websites and not university["is_sample"]:
            st.link_button(
                "🌐 Visit official website",
                websites[0],
                width="stretch",
            )
        elif university["is_sample"]:
            st.button("🌐 Website (sample only)", disabled=True, width="stretch")
        else:
            st.button("🌐 Website not published", disabled=True, width="stretch")

    # --- Favorite ---------------------------------------------------------
    with col2:
        saved = state.is_favorite(uni_id)
        if st.button(
            "★ Saved to favorites" if saved else "☆ Add to favorites",
            width="stretch",
            type="secondary" if saved else "primary",
        ):
            state.toggle_favorite(uni_id)
            st.rerun()

    # --- Compare ----------------------------------------------------------
    with col3:
        if st.button("⚖️ Compare this university", width="stretch"):
            if uni_id not in st.session_state["compare_ids"]:
                st.session_state["compare_ids"].append(uni_id)
            st.switch_page("pages/compare.py")


def render_facts(university: dict):
    """Address, contact details and the yearly fee."""
    col_left, col_right = st.columns([3, 2], gap="medium")

    with col_left:
        with st.container(border=True):
            style.section_title("Address and contact")

            st.write(f"**Address:** {university['address'] or 'Not published'}")

            phones = split_values(university["tel"])
            st.write(f"**Phone:** {', '.join(phones) if phones else 'Not published'}")

            emails = split_values(university["email"])
            st.write(f"**Email:** {', '.join(emails) if emails else 'Not published'}")

            websites = split_values(university["website"])
            if websites:
                st.write("**Website:** " + ", ".join(websites))
            else:
                st.write("**Website:** Not published")

            st.write(f"**Rector:** {university['rector'] or 'Not published'}")

    with col_right:
        with st.container(border=True):
            style.section_title("Yearly tuition fee")

            fee = data.format_tuition(university["id"])
            if fee == data.FEE_NOT_PUBLISHED:
                st.metric("Fee", "Not published")
                st.caption(
                    "The Ministry of Education data does not include tuition "
                    "fees. Please contact the university directly."
                )
            else:
                st.metric("Fee (per year)", fee)
                st.caption("Sample data - these fees are invented, not real.")


def render_majors(university: dict):
    """The list of majors / faculties, with fees when we have them."""
    majors_table = data.get_majors_for(university["id"])

    style.section_title(
        f"Majors offered ({len(university['majors'])})",
        "These come from the faculty list published by the Ministry of Education.",
    )

    if majors_table.empty:
        st.write("No majors listed for this university.")
        return

    # Build a small, readable table.
    shown = majors_table[["major", "degree_level", "annual_tuition_usd"]].copy()
    shown.columns = ["Major / faculty", "Level", "Yearly fee (USD)"]
    # Replace missing fees with clear words instead of an empty cell.
    shown["Yearly fee (USD)"] = shown["Yearly fee (USD)"].map(
        lambda value: data.FEE_NOT_PUBLISHED if pd.isna(value) else f"${float(value):,.0f}"
    )

    st.dataframe(shown, width="stretch", hide_index=True)


def render_source(university: dict):
    """Where this information came from, and the warning to double-check it."""
    style.section_title("Where this information comes from")

    st.write(f"**Source:** {university['source']}")
    st.write(f"**Data year:** {university['source_year']}")
    if university["last_update"]:
        st.write(f"**File last updated:** {university['last_update']}")

    st.warning(
        "This information may be out of date. Majors, fees and admission "
        "requirements change every year. **Please confirm the details directly "
        "with the university before you apply.**"
    )


def render_detail_page():
    """Draw the whole Detail page."""
    university_id = state.get_selected_university()

    if not university_id:
        render_empty_state()
        style.site_footer()
        return

    university = data.get_university(university_id)

    # The id might be wrong (for example an old link that was pasted).
    if university is None:
        st.title("🏫 University details")
        st.error("We could not find that university.")
        st.write("It may have been removed, or the link may be incorrect.")
        if st.button("Go to Explore", type="primary"):
            st.switch_page("pages/browse.py")
        style.site_footer()
        return

    # A small "back" link at the top.
    if st.button("← Back to Explore"):
        st.switch_page("pages/browse.py")

    render_header(university)
    render_actions(university)
    render_facts(university)
    render_majors(university)
    render_source(university)
    style.site_footer()


render_detail_page()

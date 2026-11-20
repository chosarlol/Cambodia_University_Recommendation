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


def render_actions(university: dict):
    """The buttons: official website, favorite, compare."""
    uni_id = university["id"]
    col1, col2, col3 = st.columns(3)

    # --- Official website -------------------------------------------------
    with col1:
        websites = split_values(university["website"])
        if websites:
            st.link_button(
                "🌐 Visit official website",
                websites[0],
                width="stretch",
            )
        else:
            st.button("🌐 Website not published", disabled=True, width="stretch",
                      key=f"web_{uni_id}")

    # Every button has a key with the university id, because several
    # universities can be shown on this page at once (one per tab).

    # --- Favorite ---------------------------------------------------------
    with col2:
        saved = state.is_favorite(uni_id)
        if st.button(
            "★ Saved to favorites" if saved else "☆ Add to favorites",
            width="stretch",
            type="secondary" if saved else "primary",
            key=f"fav_{uni_id}",
        ):
            state.toggle_favorite(uni_id)
            st.rerun()

    # --- Compare ----------------------------------------------------------
    with col3:
        if st.button("⚖️ Compare this university", width="stretch",
                     key=f"compare_{uni_id}"):
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
                st.metric("Fee (per year)", data.format_tuition_markdown(university["id"]))
                st.caption(
                    "Lowest to highest yearly fee across the majors below. "
                    f"Fees in riel are converted at {data.KHR_PER_USD:,} riel = 1 USD."
                )
                for source in data.get_fee_sources(university["id"]):
                    st.caption(f"Source: {source}")

        render_shifts(university)


def render_shifts(university: dict):
    """
    When you can study here: morning, afternoon, evening or weekend.

    This matters a lot for students who work during the day. The Ministry file
    does not contain it, so we show only what we checked ourselves and say
    plainly when we have not checked yet.
    """
    info = data.get_shifts(university["id"])

    with st.container(border=True):
        style.section_title("When you can study")

        if info["known"]:
            st.write(f"**Shifts:** {data.format_shifts(university['id'])}")
            if info["source"]:
                st.caption(f"Checked against: {info['source']}")
            if info["checked_on"]:
                st.caption(f"Checked on: {info['checked_on']}")
        else:
            st.write(f"**Shifts:** {data.SHIFT_NOT_PUBLISHED}")
            st.caption(
                "The Ministry data does not list study times and we have not "
                "confirmed this university yet. Ask them whether they run "
                "morning, afternoon, evening or weekend classes."
            )


def render_majors(university: dict):
    """The list of majors / faculties, with fees when we have them."""
    majors_table = data.get_majors_for(university["id"])

    # True when our team collected this university's majors (data/major_detail/).
    collected = (
        not majors_table.empty
        and (majors_table["source"] != data.PUBLIC_SOURCE).all()
    )

    style.section_title(
        f"Majors offered ({len(university['majors'])})",
        "Majors and fees collected by our team."
        if collected
        else "These come from the faculty list published by the Ministry of Education.",
    )

    if majors_table.empty:
        st.write("No majors listed for this university.")
        return

    def money(value, unit: str) -> str:
        """A fee as text, or clear words instead of an empty cell."""
        if pd.isna(value):
            return data.FEE_NOT_PUBLISHED
        return f"${float(value):,.0f}" if unit == "USD" else f"{float(value):,.0f} riel"

    if not collected:
        shown = pd.DataFrame(
            {
                "Major / faculty": majors_table["major"],
                "Level": majors_table["degree_level"],
                "Yearly fee (USD)": majors_table["annual_tuition_usd"].map(
                    lambda v: money(v, "USD")
                ),
            }
        )
        st.dataframe(shown, width="stretch", hide_index=True)
        return

    # Let the visitor narrow a long list down to one faculty.
    faculties = sorted(f for f in majors_table["faculty"].unique() if f)
    if len(faculties) > 1:
        chosen = st.selectbox("Faculty", ["All faculties"] + faculties,
                              key=f"faculty_{university['id']}")
        if chosen != "All faculties":
            majors_table = majors_table[majors_table["faculty"] == chosen]

    def fee_range(row) -> str:
        """'$450' or '$450 - $600' (fee depends on the year of study)."""
        low, high = row["annual_tuition_usd"], row["annual_tuition_usd_max"]
        if pd.isna(low):
            return data.FEE_NOT_PUBLISHED
        if pd.isna(high) or high == low:
            return money(low, "USD")
        return f"{money(low, 'USD')} - {money(high, 'USD')}"

    # Every column we may have. A column that is empty for this whole
    # university is dropped, so the table is not a wall of "Not published".
    columns = {
        "Major": majors_table["major"],
        "Khmer name": majors_table["major_kh"],
        "Faculty": majors_table["faculty"],
        "Level": majors_table["degree_level"].replace("Not published", ""),
        "Yearly fee (USD)": majors_table.apply(fee_range, axis=1),
        "Yearly fee (riel)": majors_table["fee_khr"].map(
            lambda v: "" if pd.isna(v) else money(v, "KHR")
        ),
        "Entrance exam": majors_table["entrance_exam"],
        "Shifts": majors_table["major_shifts"].map(
            lambda s: ", ".join(x.capitalize() for x in s)
        ),
        "Places": majors_table["places_total"].map(
            lambda p: "" if pd.isna(p) else f"{p:,.0f}"
        ),
        "Notes": majors_table["notes"],
    }
    shown = pd.DataFrame(
        {
            name: values
            for name, values in columns.items()
            if name in ("Major", "Yearly fee (USD)") or (values != "").any()
        }
    )
    st.dataframe(shown, width="stretch", hide_index=True)

    # General notes for the whole university (discounts, scholarships...).
    for note in university.get("detail_notes") or []:
        st.info(note.replace("$", "\\$"))
    sources = sorted(majors_table["source"].unique())
    st.caption("Source: " + "; ".join(sources))


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


def render_one_university(university: dict):
    """Everything about one university, top to bottom."""
    render_header(university)
    render_actions(university)
    render_facts(university)
    render_majors(university)
    render_source(university)


def render_detail_page():
    """
    Draw the whole Detail page.

    One university: shown as before. Several (ticked on the Explore page):
    one tab per university, each with the same full details.
    """
    chosen_ids = state.get_selected_universities()

    if not chosen_ids:
        render_empty_state()
        style.site_footer()
        return

    # Ids might be wrong (for example an old link that was pasted).
    universities = [data.get_university(uid) for uid in chosen_ids]
    universities = [u for u in universities if u is not None]

    if not universities:
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

    if len(universities) == 1:
        render_one_university(universities[0])
    else:
        st.caption(
            f"You chose **{len(universities)} universities**. "
            "Click a tab to see each one."
        )
        tabs = st.tabs([u["name"] for u in universities])
        for tab, university in zip(tabs, universities):
            with tab:
                render_one_university(university)

    style.site_footer()


render_detail_page()

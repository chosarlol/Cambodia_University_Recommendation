"""
Explore / Browse Universities page.

Shows every university in a table, with filters for type, province and major,
plus a search box for the name. Each result also has an "Add to favorites"
button.

The search text typed on the Home page arrives here through
st.session_state["search_text"], so nothing the visitor typed is lost.
"""

import streamlit as st

from services import data
from utils import state, style
from utils.validation import ANY_PROVINCE

# How many result cards to show at once, so the page stays fast and readable.
RESULTS_PER_PAGE = 10


def render_filters():
    """
    Draw the filter controls and return what the visitor chose.

    Returns a dictionary: name_query, types, provinces, majors.
    """
    # The search box starts with whatever was typed on the Home page.
    name_query = st.text_input(
        "Search by university name",
        value=state.get_search_text(),
        placeholder="For example: Royal University",
        key="browse_name_query",
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        types = st.multiselect(
            "Type",
            options=data.list_types(),
            default=[],
            placeholder="Public and Private",
        )

    with col2:
        provinces = st.multiselect(
            "Province",
            options=data.list_provinces(),
            default=[],
            placeholder="All provinces",
        )

    with col3:
        majors = st.multiselect(
            "Major / faculty",
            options=data.list_majors(),
            default=[],
            placeholder="All majors",
        )

    return {
        "name_query": name_query,
        "types": types,
        "provinces": provinces,
        "majors": majors,
    }


def render_results_table(results):
    """
    Show the matching universities as one table that is easy to scan.

    The visitor ticks one or more rows, then presses the blue button to open
    those universities. The Detail page shows each one in its own tab.
    """
    table = results[["name", "type", "province", "established_year"]].copy()
    table.columns = ["University", "Type", "Province", "Founded"]
    table["Majors"] = results["majors"].map(len)
    table["Yearly fee"] = results["id"].map(data.format_tuition)

    # When we come back from a university page, start with no ticked rows.
    if st.session_state.pop("reset_browse_selection", False):
        st.session_state.pop("browse_table", None)

    event = st.dataframe(
        table,
        width="stretch",
        hide_index=True,
        key="browse_table",
        on_select="rerun",          # rerun when a box is ticked, to update the button
        selection_mode="multi-row",
    )

    ticked_rows = event.selection.rows
    count = len(ticked_rows)
    if count == 0:
        label = "Open selected universities"
    elif count == 1:
        label = "Open 1 selected university"
    else:
        label = f"Open {count} selected universities"

    col_button, col_hint = st.columns([2, 3], vertical_alignment="center")
    with col_button:
        clicked = st.button(
            label,
            type="primary",             # the blue button
            icon=":material/open_in_new:",
            disabled=count == 0,
            width="stretch",
            key="open_selected",
        )
    with col_hint:
        st.caption(
            "Tick the box next to one or more universities, then press the button."
            if count == 0
            else "Each university opens in its own tab."
        )

    if clicked and count:
        # Keep the order the universities have in the table.
        state.open_universities([results.iloc[row]["id"] for row in sorted(ticked_rows)])
        st.session_state["reset_browse_selection"] = True
        st.switch_page("pages/detail.py")


def render_result_card(university):
    """
    Show one university as a small card with a favorites button.

    `university` is one row of the table, used like a dictionary.
    """
    uni_id = university["id"]

    with st.container(border=True):
        col_text, col_button = st.columns([4, 1], vertical_alignment="center")

        with col_text:
            # The name is a button, so clicking it opens the university page.
            if st.button(
                university["name"],
                key=f"open_{uni_id}",
                type="tertiary",       # tertiary = looks like a link, not a box
            ):
                state.open_university(uni_id)
                st.session_state["reset_browse_selection"] = True
                st.switch_page("pages/detail.py")

            # Show the Khmer name only when the data actually has one.
            if university.get("name_kh"):
                st.markdown(f"**{university['name_kh']}**")

            fee = data.format_tuition_markdown(uni_id)
            st.caption(
                f"{university['type']} · {university['province']} · "
                f"{len(university['majors'])} majors · {fee}"
            )

            # The first few majors, so the visitor sees what is offered.
            preview = ", ".join(university["majors"][:4])
            if len(university["majors"]) > 4:
                preview += ", ..."
            st.write(preview if preview else "No majors listed.")

        with col_button:
            saved = state.is_favorite(uni_id)
            label = "★ Saved" if saved else "☆ Favorite"
            if st.button(label, key=f"fav_{uni_id}", width="stretch"):
                state.toggle_favorite(uni_id)
                st.rerun()


def render_browse_page():
    """Draw the whole Explore page."""
    # Stop with a friendly message if the data files are missing.
    missing = data.missing_data_files()
    if missing:
        st.error("#### The university data could not be loaded")
        st.write("These files are missing from `data/raw/`:")
        for name in missing:
            st.write(f"- `{name}`")
        return

    st.title("🧭 Explore universities")
    st.caption(
        "Filter the list, or search by name. **Tick one or more universities "
        "and press Open** to see their majors and fees. Use ☆ Favorite to keep "
        "one for later."
    )

    filters = render_filters()

    # Keep the search box and the Home page search box in step.
    state.set_search_text(filters["name_query"])

    # All filtering happens inside services/data.py.
    results = data.search_universities(
        name_query=filters["name_query"],
        types=filters["types"],
        provinces=filters["provinces"],
        majors=filters["majors"],
    )

    st.divider()

    # --- No matches ---------------------------------------------------------
    if results.empty:
        st.warning("No university matches these filters.")
        st.write("Try removing one filter, or search for a shorter word.")
        if st.button("Clear all filters"):
            state.set_search_text("")
            st.rerun()
        style.site_footer()
        return

    # --- Results -----------------------------------------------------------
    saved_count = len(state.get_favorites())
    header = f"**{len(results)}** universities found"
    if saved_count:
        header += f" · **{saved_count}** saved in your favorites"
    st.markdown(header)

    render_results_table(results)

    style.section_title("Results in detail")

    # Show the first page of cards, with a button to show more.
    shown = st.session_state.get("browse_shown", RESULTS_PER_PAGE)
    for _, university in results.head(shown).iterrows():
        render_result_card(university)

    if shown < len(results):
        remaining = len(results) - shown
        if st.button(f"Show {min(RESULTS_PER_PAGE, remaining)} more"):
            st.session_state["browse_shown"] = shown + RESULTS_PER_PAGE
            st.rerun()

    style.site_footer()


render_browse_page()

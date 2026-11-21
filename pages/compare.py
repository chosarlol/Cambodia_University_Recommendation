"""
Compare page.

Pick 2 or 3 universities and see them side by side.
NOTE: the full side-by-side table is built in a later step. For now the page
lets you choose universities and shows the basic facts next to each other.
"""

import streamlit as st

from services import data
from utils import state, style

st.title("⚖️ Compare universities")
st.caption("Choose 2 or 3 universities to see them side by side.")

# Every university, through the data layer as usual - never a CSV directly.
universities = data.load_universities()

# The dropdown must SHOW the names, but the rest of the app works with ids.
# This dictionary lets us turn the chosen name back into its id.
name_to_id = dict(zip(universities["name"], universities["id"]))

chosen_names = st.multiselect(
    "Universities to compare",
    options=list(name_to_id.keys()),
    max_selections=3,          # more than 3 columns is unreadable on a phone
    placeholder="Start typing a university name",
)

# --- Not enough chosen yet -------------------------------------------------
# Comparing needs at least two, so we say so rather than showing one lonely
# column or an empty page.
if len(chosen_names) < 2:
    st.info("Choose at least 2 universities to start comparing.")

# --- One column per chosen university -------------------------------------
else:
    # As many columns as universities picked: 2 or 3.
    columns = st.columns(len(chosen_names), gap="medium")

    for column, name in zip(columns, chosen_names):
        uni_id = name_to_id[name]
        university = data.get_university(uni_id)

        with column:
            with st.container(border=True):
                st.markdown(f'<div class="card-title">{name}</div>',
                            unsafe_allow_html=True)
                # The same facts in the same order in every column, so the
                # visitor can compare straight across the page.
                st.write(f"**Type:** {university['type']}")
                st.write(f"**Province:** {university['province']}")
                # "or 'Not published'" catches an empty year: we say so
                # instead of printing a blank space or guessing a date.
                st.write(f"**Founded:** {university['established_year'] or 'Not published'}")
                st.write(f"**Yearly fee:** {data.format_tuition_markdown(uni_id)}")
                st.write(f"**Majors:** {len(university['majors'])}")
                # The full list is long, so it stays folded until asked for.
                with st.expander("See all majors"):
                    for major in university["majors"]:
                        st.write(f"- {major}")

style.site_footer()

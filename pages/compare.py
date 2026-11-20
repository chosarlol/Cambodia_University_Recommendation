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

universities = data.load_universities()

# A dictionary so the dropdown shows names but we keep the ids.
name_to_id = dict(zip(universities["name"], universities["id"]))

chosen_names = st.multiselect(
    "Universities to compare",
    options=list(name_to_id.keys()),
    max_selections=3,
    placeholder="Start typing a university name",
)

if len(chosen_names) < 2:
    st.info("Choose at least 2 universities to start comparing.")
else:
    columns = st.columns(len(chosen_names), gap="medium")

    for column, name in zip(columns, chosen_names):
        uni_id = name_to_id[name]
        university = data.get_university(uni_id)

        with column:
            with st.container(border=True):
                st.markdown(f'<div class="card-title">{name}</div>',
                            unsafe_allow_html=True)
                st.write(f"**Type:** {university['type']}")
                st.write(f"**Province:** {university['province']}")
                st.write(f"**Founded:** {university['established_year'] or 'Not published'}")
                st.write(f"**Yearly fee:** {data.format_tuition_markdown(uni_id)}")
                st.write(f"**Majors:** {len(university['majors'])}")
                with st.expander("See all majors"):
                    for major in university["majors"]:
                        st.write(f"- {major}")

style.site_footer()

"""
My Favorites page.

The saved universities are kept in st.session_state["favorites"] (see
utils/state.py), so they last while the browser tab is open. A database
comes later in the course.
"""

import streamlit as st

from services import data
from utils import state, style

st.title("❤️ My favorites")

favorite_ids = state.get_favorites()

if not favorite_ids:
    st.info("You have not saved any universities yet.")
    st.write("Use the ☆ Favorite button on the Explore page to save one.")
    if st.button("Go to Explore", type="primary"):
        st.switch_page("pages/browse.py")
else:
    st.caption(f"{len(favorite_ids)} saved. They stay here while this tab is open.")

    saved = data.get_universities_by_ids(favorite_ids)

    for _, university in saved.iterrows():
        uni_id = university["id"]
        with st.container(border=True):
            col_text, col_button = st.columns([4, 1], vertical_alignment="center")
            with col_text:
                # Clicking the name opens that university's own page.
                if st.button(university["name"], key=f"fav_open_{uni_id}",
                             type="tertiary"):
                    state.open_university(uni_id)
                    st.switch_page("pages/detail.py")
                st.caption(
                    f"{university['type']} · {university['province']} · "
                    f"{data.format_tuition_markdown(uni_id)}"
                )
            with col_button:
                if st.button("Remove", key=f"unfav_{uni_id}", width="stretch"):
                    state.remove_favorite(uni_id)
                    st.rerun()

    if st.button("Clear all favorites"):
        state.clear_favorites()
        st.rerun()

style.site_footer()

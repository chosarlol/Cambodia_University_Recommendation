"""
Results page - the ranked list of universities.

NOTE FOR THE NEXT STEP:
The ranking function (services/recommend.py) is not written yet. For now this
page proves that the answers from the form arrived safely in st.session_state,
and shows the universities that simply match the filters. The match score and
the reasons come in the next step.
"""

import streamlit as st

from services import data
from utils import state, style, validation
from utils.validation import ANY_PROVINCE, NOT_SURE

st.title("📋 Your results")

# Everything on this page comes from the answers the visitor gave in the form.
# They were saved into st.session_state by utils/forms.py.
profile = state.get_profile()

# --- Nobody has filled in the form yet ------------------------------------
# st.stop() below ends the script here, so the rest of the page never runs
# and we do not have to indent everything that follows inside an "else".
if not profile:
    st.info("You have not told us what you are looking for yet.")
    st.write("Fill in the short form and your ranked list will appear here.")
    if st.button("Go to the form", type="primary"):
        st.switch_page("pages/recommend.py")
    style.site_footer()
    st.stop()

# --- Friendly summary of what the visitor asked for -----------------------
# The name is optional in the form, so we greet by name only when we have one.
greeting = f"Here are your matches, {profile['name']}." if profile.get("name") else "Here are your matches."
st.subheader(greeting)
st.markdown(f"You are looking for {validation.describe_profile(profile)}.")

col_edit, col_clear = st.columns([1, 3])
with col_edit:
    if st.button("✏️ Change my answers"):
        st.switch_page("pages/recommend.py")

st.divider()

# This warning is deliberate and must stay until services/recommend.py exists.
# A placeholder has to say on screen that it is a placeholder: showing invented
# scores would be worse than showing none.
st.warning(
    "**Ranking is not built yet.** This step only confirms that your answers "
    "were saved. The match score and the reasons for each result are the next "
    "step of the project. Below is a simple filtered list in the meantime."
)

# --- A simple filtered list, using only existing data functions -----------
# "Either" and "Any province" mean: do not filter on that field.
chosen_types = [] if profile["uni_type"] == "Either" else [profile["uni_type"]]
chosen_provinces = [] if profile["province"] == ANY_PROVINCE else [profile["province"]]
chosen_majors = [] if profile["major"] == NOT_SURE else [profile["major"]]

results = data.search_universities(
    types=chosen_types,
    provinces=chosen_provinces,
    majors=chosen_majors,
)

if results.empty:
    st.error("No university matches all of your choices.")
    st.write(
        "Try choosing **Either** for the type, **Any province**, or "
        "**Not sure yet** for the major."
    )
else:
    st.markdown(f"**{len(results)}** universities match your choices so far.")

    for _, university in results.iterrows():
        uni_id = university["id"]
        with st.container(border=True):
            col_text, col_button = st.columns([4, 1], vertical_alignment="center")
            with col_text:
                # Clicking the name opens that university's own page.
                if st.button(university["name"], key=f"res_open_{uni_id}",
                             type="tertiary"):
                    state.open_university(uni_id)
                    st.switch_page("pages/detail.py")
                st.caption(
                    f"{university['type']} · {university['province']} · "
                    f"{data.format_tuition_markdown(uni_id)}"
                )
            with col_button:
                saved = state.is_favorite(uni_id)
                if st.button("★ Saved" if saved else "☆ Favorite",
                             key=f"res_fav_{uni_id}", width="stretch"):
                    state.toggle_favorite(uni_id)
                    st.rerun()

style.site_footer()

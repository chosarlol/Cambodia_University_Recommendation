"""
Find My University page.

This is the same form as the quick form on the Home page, just with more room
and a short explanation. Both pages call utils/forms.py, so there is only one
copy of the form in the project.
"""

import streamlit as st

from services import data
from utils import forms, state, style

missing = data.missing_data_files()
if missing:
    st.error("#### The university data could not be loaded")
    st.write("These files are missing from `data/raw/`:")
    for file_name in missing:
        st.write(f"- `{file_name}`")
else:
    st.title("🎯 Find my university")
    st.caption(
        "Tell us what you are looking for. We score every university in the "
        "database and explain why each one matched."
    )

    profile = state.get_profile()
    if profile:
        forms.render_welcome_back(profile)

    forms.render_recommendation_form(form_key="main_recommendation_form")

    style.site_footer()

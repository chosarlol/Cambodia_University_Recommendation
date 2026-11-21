"""
Find My University page.

This is the same form as the quick form on the Home page, just with more room
and a short explanation. Both pages call utils/forms.py, so there is only one
copy of the form in the project.
"""

import streamlit as st

from services import data
from utils import forms, state, style

# --- Check the data is there before drawing anything ----------------------
# The form offers provinces and majors read from the data files. Without them
# the dropdowns would be empty, so we say what is wrong instead.
missing = data.missing_data_files()
if missing:
    st.error("#### The university data could not be loaded")
    st.write("These files are missing from `data/raw/`:")
    for file_name in missing:
        st.write(f"- `{file_name}`")

# --- The page itself -------------------------------------------------------
else:
    st.title("🎯 Find my university")
    st.caption(
        "Tell us what you are looking for. We score every university in the "
        "database and explain why each one matched."
    )

    # A visitor who already filled the form gets a "welcome back" line
    # showing what they chose last time, so they need not start again.
    profile = state.get_profile()
    if profile:
        forms.render_welcome_back(profile)

    # The form itself lives in utils/forms.py because the Home page shows the
    # very same form. The key must differ from the Home page's key, or
    # Streamlit treats the two forms as one and they overwrite each other.
    forms.render_recommendation_form(form_key="main_recommendation_form")

    style.site_footer()

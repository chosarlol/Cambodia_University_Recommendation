"""
About / Data Sources page.

Explains where every number on the website comes from, and warns the visitor
that they must check the details with the university themselves.
"""

import streamlit as st

from services import data
from utils import style

st.title("ℹ️ About this website")

st.write(
    "**Cambodia University Recommendation** helps high school graduates in "
    "Cambodia find a university that matches their major, province and budget. "
    "It is a student project for the course *Web Application Development for "
    "Data Science*, Year 3 Data Science, Royal University of Phnom Penh."
)

# --- The counts -----------------------------------------------------------
# Read from the data, never typed in by hand, so the page cannot go out of
# date when a university is added or removed.
stats = data.get_summary_stats()

style.section_title("What is in the database")
col1, col2, col3 = st.columns(3)
col1.metric("Universities", stats["total"])
col2.metric("Public", stats["public"])
col3.metric("Private", stats["private"])

# --- Layer 1: the official Ministry data ----------------------------------
style.section_title("Where the data comes from")

st.markdown(
    """
**Real data - public universities**

- **Source:** Ministry of Education, Youth and Sport (MOEYS), Cambodia
- **Document:** `MOEYS_KH__15.08.2017.pdf`
- **Year:** 2017, with the data file last updated **02/07/2018**
- **Contains:** 29 public universities - name, website, email, phone,
  location, rector, year founded, and the faculties each one offers
- **Map coordinates** come from the matching MOEYS KML file
"""
)

# --- Layer 2: what our own team collected ---------------------------------
# These numbers also come from the data layer, so this paragraph tells the
# truth about how far the collection has got, even while it is still growing.
progress = data.get_collection_progress()
st.markdown(
    f"""
**Collected by our team - majors and fees**

The MOEYS data contains **no tuition fees** and only broad faculty names. For
**{len(progress["with_majors"])} of the {progress["total"]} public universities**
our team collected the real majors with their Khmer names, and for
**{len(progress["with_fees"])}** of them the yearly fees. RUPP's list also has
entrance exam subjects and places per shift. The files are in
`data/major_detail/`. Fees given in riel are converted at 4,100 riel = 1 USD.

- Public universities we have not collected yet show **"Fee not published"**,
  because we never guess a number

**Private universities - not added yet**

The MOEYS data contains **no private universities**, and our team has not
collected any yet, so the site currently lists public universities only.
"""
)

style.section_title("A newer file we chose not to use")
st.write(
    "A 2021 MOEYS file with 37 universities also exists, but it is damaged: "
    "its column names are shifted by two positions, and the university name "
    "and website were saved as `0` for every row. Matching by email address "
    "recovered only 26 of the 37 names. Rather than guess the missing names, "
    "this website uses the complete 2018 dataset instead."
)

style.section_title("Important warning")
st.warning(
    "This information is from 2017/2018 and may be out of date. Majors, fees "
    "and admission requirements change every year. **Always confirm the "
    "details directly with the university before you apply.**"
)

style.site_footer()

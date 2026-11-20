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

stats = data.get_summary_stats()

style.section_title("What is in the database")
col1, col2, col3 = st.columns(3)
col1.metric("Universities", stats["total"])
col2.metric("Real (public)", stats["real_rows"])
col3.metric("Sample (private)", stats["sample_rows"])

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

st.markdown(
    """
**Sample data - private universities and all tuition fees**

The MOEYS data contains **no tuition fees and no private universities**.
To be able to build and test the search, ranking and compare features, this
website includes **invented** private universities and fees.

- Every sample university name starts with **`SAMPLE -`**
- Every fee shown on this site is **not real**
- Real public universities always show **"Fee not published"**, because we
  never guess a number
"""
)

st.error(
    "**Do not use the sample numbers for a real decision.** They exist only so "
    "the interface can be demonstrated."
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

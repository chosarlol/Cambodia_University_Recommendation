"""
All the custom look-and-feel of the website is kept in this one file.

Why one file?
So that changing a colour or a spacing is done in a single place, and every
page looks the same. Pages only need to call `apply_style()` once at the top.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Colours used across the whole site. Change them here only.
# (They match the values in .streamlit/config.toml.)
# ---------------------------------------------------------------------------
BLUE = "#1a56db"        # main brand colour (buttons, links)
DARK_BLUE = "#15317e"   # headings and the hero background
GOLD = "#f0b429"        # small accent colour
GREY_TEXT = "#5b6779"   # soft grey for secondary text
LIGHT_BG = "#f5f7fb"    # page background for cards and sections


# The CSS below is plain web styling. Streamlit lets us inject it as HTML.
CUSTOM_CSS = f"""
<style>
/* ---------- 1. Hide the parts of Streamlit we do not need ---------- */
/* NOTE: we do NOT hide the whole header, because the top navigation
   menu lives inside it. We only hide the menu button and the footer. */
[data-testid="stMainMenu"] {{ visibility: hidden; }}
[data-testid="stAppDeployButton"] {{ display: none; }}
[data-testid="stStatusWidget"] {{ display: none; }}
footer {{ visibility: hidden; height: 0; }}

/* ---------- 2. Page spacing ---------- */
.block-container {{
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1150px;
}}

/* ---------- 3. The hero (big blue banner at the top of Home) ---------- */
.hero {{
    background: linear-gradient(135deg, {DARK_BLUE} 0%, {BLUE} 100%);
    color: #ffffff;
    border-radius: 18px;
    padding: 46px 40px 40px 40px;
    margin-bottom: 26px;
}}
.hero h1 {{
    color: #ffffff;
    font-size: 2.5rem;
    line-height: 1.15;
    margin: 0 0 12px 0;
    font-weight: 700;
}}
.hero p {{
    color: #dbe5ff;
    font-size: 1.08rem;
    margin: 0;
    max-width: 640px;
}}
.hero .accent {{ color: {GOLD}; }}

/* ---------- 4. Section titles ---------- */
.section-title {{
    font-size: 1.45rem;
    font-weight: 700;
    color: {DARK_BLUE};
    margin: 30px 0 6px 0;
}}
.section-subtitle {{
    color: {GREY_TEXT};
    margin: 0 0 14px 0;
    font-size: 0.97rem;
}}

/* ---------- 5. Cards (Streamlit containers with border=True) ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 14px;
    border: 1px solid #e3e8f0;
    background: #ffffff;
    box-shadow: 0 1px 3px rgba(20, 40, 80, 0.06);
}}
.card-icon {{ font-size: 2rem; line-height: 1; }}
.card-title {{
    font-size: 1.18rem;
    font-weight: 700;
    color: {DARK_BLUE};
    margin: 8px 0 4px 0;
}}
.card-text {{
    color: {GREY_TEXT};
    font-size: 0.95rem;
    min-height: 62px;
    margin-bottom: 8px;
}}

/* ---------- 6. Buttons ---------- */
.stButton > button {{
    border-radius: 9px;
    font-weight: 600;
    padding: 0.5rem 1rem;
}}

/* A "tertiary" button is used for a university name, so it should look
   like a clickable title, not like a box. */
.stButton > button[kind="tertiary"] {{
    font-size: 1.18rem;
    font-weight: 700;
    color: {DARK_BLUE};
    padding: 0 0 2px 0;
    text-align: left;
}}
.stButton > button[kind="tertiary"]:hover {{
    color: {BLUE};
    text-decoration: underline;
}}

/* Show a hand cursor on table rows, because clicking one opens a page. */
[data-testid="stDataFrame"] div[role="row"] {{ cursor: pointer; }}

/* ---------- 7. "How it works" steps ---------- */
.step-number {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 34px; height: 34px;
    border-radius: 50%;
    background: {BLUE};
    color: #ffffff;
    font-weight: 700;
    margin-bottom: 8px;
}}

/* ---------- 8. Footer ---------- */
.site-footer {{
    margin-top: 42px;
    padding-top: 20px;
    border-top: 1px solid #e3e8f0;
    color: {GREY_TEXT};
    font-size: 0.87rem;
    line-height: 1.6;
}}
.site-footer strong {{ color: {DARK_BLUE}; }}

/* ---------- 9. Phone-sized screens ---------- */
@media (max-width: 640px) {{
    .hero {{ padding: 28px 20px; }}
    .hero h1 {{ font-size: 1.75rem; }}
    .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
    .card-text {{ min-height: 0; }}
}}
</style>
"""


def apply_style():
    """Add the custom CSS to the page. Call this once at the top of every page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def section_title(title: str, subtitle: str = ""):
    """Show a consistent section heading, with an optional grey line under it."""
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def card_header(icon: str, title: str, text: str):
    """Show the icon + title + description part of a card."""
    st.markdown(
        f'<div class="card-icon">{icon}</div>'
        f'<div class="card-title">{title}</div>'
        f'<div class="card-text">{text}</div>',
        unsafe_allow_html=True,
    )


def site_footer():
    """The same footer on every page."""
    st.markdown(
        """
        <div class="site-footer">
        <strong>Data sources:</strong> Public university information comes from the
        Ministry of Education, Youth and Sport (MOEYS), Cambodia -
        document <em>MOEYS_KH__15.08.2017.pdf</em>, file last updated 02/07/2018.
        Private universities and all tuition fees shown on this site are
        <strong>sample (invented) data</strong> used for testing; their names start
        with "SAMPLE -".<br><br>
        <strong>Please note:</strong> this information may be out of date. Always
        confirm majors, fees and admission requirements directly with the
        university before you apply.<br><br>
        Cambodia University Recommendation - student project for
        <em>Web Application Development for Data Science</em>,
        Year 3 Data Science, Royal University of Phnom Penh.
        </div>
        """,
        unsafe_allow_html=True,
    )

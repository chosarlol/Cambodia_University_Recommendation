"""
Cambodia University Recommendation - entry point and landing page.

Run the app with:   streamlit run app.py

This file does three jobs:
  1. sets up the page and the top navigation bar,
  2. keeps the visitor's answers in st.session_state,
  3. draws the Home (landing) page.

All data comes from services/data.py. This file never opens a data file itself.
"""

import streamlit as st

from services import data
from utils import forms, state, style

# This must be the very first Streamlit command.
st.set_page_config(
    page_title="Cambodia University Recommendation",
    page_icon="🎓",
    layout="wide",
)


# ---------------------------------------------------------------------------
# 1. Small helper functions used by the Home page
#    (the session_state keys themselves live in utils/state.py)
# ---------------------------------------------------------------------------

def show_data_problem(missing_files: list):
    """Friendly message shown when the data files are not where we expect them."""
    st.error("#### The university data could not be loaded")
    st.write(
        "The website needs its data files, but these are missing from the "
        "`data/raw/` folder:"
    )
    for name in missing_files:
        st.write(f"- `{name}`")
    st.info(
        "Put the files back in `data/raw/` and refresh this page. "
        "Nothing else on the site will work until then."
    )


# ---------------------------------------------------------------------------
# 2. The pieces of the Home page, one function each
# ---------------------------------------------------------------------------

# The photos behind the hero banner. They change every HERO_SECONDS seconds,
# and the name of the university in the photo is shown bottom right as a
# button that opens that university's page. To add or swap a photo, put it in
# assets/hero/ and edit this list (university_id must match the app's ids).
HERO_SLIDES = [
    {
        "image": "assets/hero/rule.jpg",
        "university_id": "royal-university-of-law-and-economics",
        "label": "Royal University of Law and Economics",
    },
    {
        "image": "assets/hero/rupp.jpg",
        "university_id": "royal-university-of-phnom-penh",
        "label": "Royal University of Phnom Penh",
    },
    {
        "image": "assets/hero/rufa.jpg",
        "university_id": "royal-university-of-fine-arts",
        "label": "Royal University of Fine Arts",
    },
]
HERO_SECONDS = 10


@st.cache_data
def _image_as_data_url(path: str) -> str:
    """
    Read a photo and return it as a 'data:' URL.
    st.markdown cannot load a local file by its path, so the picture is put
    inside the page itself. Cached, so each file is read only once.
    """
    import base64
    from pathlib import Path

    file = Path(__file__).parent / path
    if not file.exists():
        return ""
    kind = "png" if file.suffix.lower() == ".png" else "jpeg"
    return f"data:image/{kind};base64," + base64.b64encode(file.read_bytes()).decode()


def _hero_slideshow_css() -> str:
    """
    CSS that stacks the photos and fades from one to the next.

    It is pure CSS (no JavaScript): every slide runs the same animation, each
    one starting HERO_SECONDS later than the one before. The button with the
    university's name runs the same animation, so the right name is always
    shown with the right photo, and a hidden button cannot be clicked.
    """
    count = len(HERO_SLIDES)
    cycle = HERO_SECONDS * count
    show = 100 / count            # % of the cycle each slide is on screen
    fade = 100 / cycle            # 1 second fade, as a % of the cycle

    rules = [
        f"""
        @keyframes heroFade {{
            0%   {{ opacity: 0; visibility: hidden; }}
            {fade:.2f}% {{ opacity: 1; visibility: visible; }}
            {show:.2f}% {{ opacity: 1; visibility: visible; }}
            {show + fade:.2f}% {{ opacity: 0; visibility: hidden; }}
            100% {{ opacity: 0; visibility: hidden; }}
        }}
        """
    ]
    for i, slide in enumerate(HERO_SLIDES):
        timing = f"heroFade {cycle}s linear {i * HERO_SECONDS}s infinite backwards"
        rules.append(
            f"""
            .hero-slide-{i} {{
                background-image: url("{_image_as_data_url(slide['image'])}");
                animation: {timing};
            }}
            .st-key-hero_link_{i} {{ animation: {timing}; }}
            """
        )
    return "<style>" + "".join(rules) + "</style>"


def render_hero():
    """The big banner with the headline, on top of changing university photos."""
    with st.container(key="hero_box"):
        slides = "".join(
            f'<div class="hero-slide hero-slide-{i}"></div>'
            for i in range(len(HERO_SLIDES))
        )
        html = _hero_slideshow_css() + f"""
            <div class="hero hero-photo">
                {slides}
                <div class="hero-shade"></div>
                <div class="hero-text">
                    <h1>Find the right university<br>in <span class="accent">Cambodia</span></h1>
                    <p>Compare public and private universities by major, province and
                    yearly budget - then save the ones you like.</p>
                </div>
            </div>
            """
        # Markdown shows indented lines after a blank line as code, so remove
        # the indentation and the empty lines before sending the HTML.
        html = "\n".join(line.strip() for line in html.splitlines() if line.strip())
        st.markdown(html, unsafe_allow_html=True)

        # One button per photo, placed bottom right by CSS (see utils/style.py).
        # A real Streamlit button keeps the visitor's favorites and answers,
        # which a plain web link would lose by reloading the site.
        for i, slide in enumerate(HERO_SLIDES):
            with st.container(key=f"hero_link_{i}"):
                if st.button(f"📍 {slide['label']}  →", key=f"hero_button_{i}"):
                    state.open_university(slide["university_id"])
                    st.switch_page("pages/detail.py")


def render_search_box():
    """Search by university name or major. Sends the visitor to the Explore page."""
    col_input, col_button = st.columns([4, 1], vertical_alignment="bottom")

    with col_input:
        query = st.text_input(
            "Search by university or major",
            value=state.get_search_text(),
            placeholder="For example: Royal University of Phnom Penh, or Agronomy",
            key="home_search_input",
        )

    with col_button:
        search_clicked = st.button("🔍 Search", width="stretch", type="primary")

    # Pressing the button saves the text, then opens the Explore page.
    if search_clicked:
        state.set_search_text(query)
        st.switch_page("pages/browse.py")


def render_path_cards():
    """The two big choices: let the site recommend, or explore on your own."""
    style.section_title(
        "How would you like to start?",
        "Pick the path that suits you. You can always switch later.",
    )

    col_a, col_b = st.columns(2, gap="medium")

    with col_a:
        with st.container(border=True):
            style.card_header(
                "🎯",
                "Recommend for me",
                "Answer four quick questions about your major, province, budget "
                "and preferred type of university. We rank the universities that "
                "fit you best and explain why.",
            )
            if st.button(
                "Start the quick form",
                width="stretch",
                type="primary",
                key="btn_path_a",
            ):
                # Streamlit cannot scroll the page, so we show a hint instead.
                st.session_state["show_form_hint"] = True
                st.rerun()

    with col_b:
        with st.container(border=True):
            style.card_header(
                "🧭",
                "I'll explore myself",
                "See every university in one table. Filter by type, province and "
                "major, search by name, and add the interesting ones to your "
                "favorites.",
            )
            if st.button(
                "Browse all universities",
                width="stretch",
                key="btn_path_b",
            ):
                st.switch_page("pages/browse.py")


def render_quick_form():
    """
    The quick recommendation form.

    The form itself lives in utils/forms.py because the "Find My University"
    page uses exactly the same one. Here we only add the heading and the hint.
    """
    style.section_title(
        "Quick recommendation form",
        "Nothing here is compulsory except your budget - choose "
        '"Not sure yet" or "No budget limit" if you do not know.',
    )

    # A short hint when the visitor arrived here from the "Recommend for me" card.
    if st.session_state["show_form_hint"]:
        st.info("You are in the right place - fill in the form below. ⬇️")

    # "Welcome back" line for a visitor who already filled the form once.
    profile = state.get_profile()
    if profile:
        forms.render_welcome_back(profile)

    forms.render_recommendation_form(form_key="quick_recommendation_form")


def render_key_numbers():
    """Four metric cards with the real counts from the data."""
    stats = data.get_summary_stats()

    style.section_title("Universities in our database")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Universities", stats["total"])
    col2.metric("Public", stats["public"])
    col3.metric("Private", stats["private"])
    col4.metric("Provinces covered", stats["provinces"])

    st.caption(
        "University details come from the Ministry of Education (MOEYS). "
        "Majors and fees were collected by our team. Private universities "
        "have not been added yet."
    )


def render_how_it_works():
    """Three short steps explaining the website."""
    style.section_title("How it works")

    steps = [
        ("1", "Tell us what you need", "Your major, province, yearly budget and the type of university you prefer."),
        ("2", "See ranked matches", "We score every university and explain each reason, such as 'within your budget'."),
        ("3", "Compare and save", "Put two or three side by side, and keep the best ones in your favorites."),
    ]

    columns = st.columns(3, gap="medium")
    for column, (number, title, text) in zip(columns, steps):
        with column:
            with st.container(border=True):
                st.markdown(
                    f'<div class="step-number">{number}</div>'
                    f'<div class="card-title">{title}</div>'
                    f'<div class="card-text">{text}</div>',
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------------------------
# 3. The Home page itself
# ---------------------------------------------------------------------------

def render_home():
    """Draw the whole landing page, section by section."""
    # Stop early with a clear message if the data files are not there.
    missing = data.missing_data_files()
    if missing:
        show_data_problem(missing)
        return

    try:
        universities = data.load_universities()
    except Exception as error:  # a broken or empty file should not crash the site
        st.error("#### The university data could not be read")
        st.write("Please check the files in `data/raw/`. Technical detail:")
        st.code(str(error))
        return

    if universities.empty:
        st.warning("The university data loaded, but it contains no rows yet.")
        return

    render_hero()
    render_search_box()
    render_path_cards()
    render_quick_form()
    render_key_numbers()
    render_how_it_works()
    style.site_footer()


# ---------------------------------------------------------------------------
# 4. Navigation - the top bar shown on every page
# ---------------------------------------------------------------------------

def build_navigation():
    """
    Create the top navigation bar.

    st.navigation(position="top") needs Streamlit 1.46 or newer. We check the
    version at runtime and fall back to the sidebar on older versions.
    """
    pages = [
        st.Page(render_home, title="Home", icon=":material/home:", default=True),
        st.Page("pages/recommend.py", title="Find My University", icon=":material/target:"),
        st.Page("pages/results.py", title="Results", icon=":material/format_list_numbered:"),
        st.Page("pages/browse.py", title="Explore", icon=":material/explore:"),
        # The Detail page is opened by clicking a university name. It has to be
        # listed here, because st.switch_page() only works for pages that are
        # part of the navigation.
        st.Page("pages/detail.py", title="University", icon=":material/school:",
                url_path="university"),
        st.Page("pages/compare.py", title="Compare", icon=":material/compare_arrows:"),
        st.Page("pages/favorites.py", title="Favorites", icon=":material/favorite:"),
        st.Page("pages/about.py", title="About", icon=":material/info:"),
    ]

    # Older Streamlit versions do not accept position="top".
    try:
        return st.navigation(pages, position="top")
    except TypeError:
        return st.navigation(pages)


def main():
    """Set up the site, then run whichever page the visitor selected."""
    state.setup_session_state()
    style.apply_style()

    # The site name/logo in the top bar, next to the navigation links.
    st.logo("assets/logo.svg", size="large")

    current_page = build_navigation()
    current_page.run()


main()

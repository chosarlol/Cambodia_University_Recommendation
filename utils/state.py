"""
The website's short-term memory.

Streamlit forgets normal Python variables on every click, so anything we want
to keep (the visitor's answers, their favorites) goes into st.session_state.
All the pages use the small functions in this file instead of touching
st.session_state directly, so the key names are written in one place only.

Later, when there is a login and a database, only this file needs to change.
"""

import streamlit as st

# The keys we use, and what they start as.
DEFAULTS = {
    "profile": None,          # answers from the recommendation form
    "search_text": "",        # text typed in the home page search box
    "favorites": [],          # list of university ids the visitor saved
    "compare_ids": [],        # universities chosen on the Compare page
    "show_form_hint": False,  # True right after "Recommend for me" is clicked
    "selected_university": None,  # the university shown on the Detail page
}


def setup_session_state():
    """Create any missing keys. Safe to call on every rerun."""
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            # list() makes a fresh copy so pages never share the same list.
            st.session_state[key] = list(value) if isinstance(value, list) else value


# ---------------------------------------------------------------------------
# The recommendation profile
# ---------------------------------------------------------------------------

def get_profile() -> dict:
    """Return the saved answers, or an empty dictionary if there are none yet."""
    return st.session_state.get("profile") or {}


def save_profile(profile: dict):
    """Remember the answers from the form."""
    st.session_state["profile"] = profile


def has_profile() -> bool:
    """True when the visitor has already filled in the form."""
    return bool(st.session_state.get("profile"))


def clear_profile():
    """Forget everything the visitor told us."""
    st.session_state["profile"] = None
    st.session_state["search_text"] = ""
    st.session_state["show_form_hint"] = False


# ---------------------------------------------------------------------------
# Favorites
# ---------------------------------------------------------------------------

def get_favorites() -> list:
    """The ids of the universities the visitor saved."""
    return st.session_state.get("favorites", [])


def is_favorite(university_id: str) -> bool:
    """True when this university is already saved."""
    return university_id in get_favorites()


def add_favorite(university_id: str):
    """Save one university (ignored if it is already saved)."""
    if university_id not in st.session_state["favorites"]:
        st.session_state["favorites"].append(university_id)


def remove_favorite(university_id: str):
    """Remove one university from the saved list."""
    if university_id in st.session_state["favorites"]:
        st.session_state["favorites"].remove(university_id)


def toggle_favorite(university_id: str):
    """Save the university if it is not saved, remove it if it is."""
    if is_favorite(university_id):
        remove_favorite(university_id)
    else:
        add_favorite(university_id)


def clear_favorites():
    """Empty the whole favorites list."""
    st.session_state["favorites"] = []


# ---------------------------------------------------------------------------
# The university shown on the Detail page
# ---------------------------------------------------------------------------

def open_university(university_id: str):
    """
    Remember which university the visitor clicked.

    We also put the id in the web address (?uni=...), so the page can be
    refreshed or the link shared and it still shows the same university.
    """
    st.session_state["selected_university"] = university_id
    st.query_params["uni"] = university_id


def get_selected_university() -> str:
    """
    Which university should the Detail page show?

    We look in session_state first, then in the web address, so a pasted
    link like .../university?uni=royal-university-of-phnom-penh still works.
    """
    chosen = st.session_state.get("selected_university")
    if chosen:
        return chosen
    return st.query_params.get("uni", "")


# ---------------------------------------------------------------------------
# Search text (shared between the Home search box and the Explore page)
# ---------------------------------------------------------------------------

def get_search_text() -> str:
    """What the visitor last searched for."""
    return st.session_state.get("search_text", "")


def set_search_text(text: str):
    """Remember a new search, so the Explore page can use it."""
    st.session_state["search_text"] = (text or "").strip()

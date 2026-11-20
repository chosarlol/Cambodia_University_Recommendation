"""
All data loading and cleaning for the Cambodia University Recommendation app.

IMPORTANT FOR THE PROJECT:
Every page gets its data by calling a function in this file. No page reads a
CSV or a KML file directly. That way, when we add a FastAPI backend later, we
only change the inside of these functions (read from an API instead of a file)
and the pages keep working without any change.

Data sources
------------
Real data   : data/raw/    - 29 public universities published by the Ministry of
                             Education, Youth and Sport (MOEYS_KH__15.08.2017.pdf,
                             file last updated 02/07/2018).
Sample data : data/sample/ - INVENTED private universities and tuition fees,
                             used only to test the interface. Every sample name
                             starts with "SAMPLE - ".
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Where the files are
# ---------------------------------------------------------------------------

# services/data.py -> services/ -> project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"
COLLECTED_DIR = PROJECT_ROOT / "data" / "collected"

PUBLIC_CSV = RAW_DIR / "public-university-of-cambodia-english-language.csv"
PUBLIC_KML = RAW_DIR / "public_universities.kml"
PRIVATE_SAMPLE_CSV = SAMPLE_DIR / "private_universities_SAMPLE.csv"
MAJORS_SAMPLE_CSV = SAMPLE_DIR / "majors_tuition_SAMPLE.csv"
SHIFTS_CSV = COLLECTED_DIR / "study_shifts.csv"

# Text we show when a fee is not in our data. We never guess a fee.
FEE_NOT_PUBLISHED = "Fee not published"

# ---------------------------------------------------------------------------
# Study shifts (morning / afternoon / evening / weekend)
# ---------------------------------------------------------------------------
# Many Cambodian students work during the day, so the shift decides whether a
# university is possible for them at all.
#
# The MOEYS file does NOT contain this information - none of its 17 columns
# mention study times. So we collect it ourselves in
# data/collected/study_shifts.csv, one row per university, each with the source
# it was checked against. A university we have not checked yet stays empty and
# the app says so; we never assume a university runs evening classes.

SHIFT_NOT_PUBLISHED = "Shift not published"

# The only values allowed in the "shifts" column of the collection file.
# Written in the order of a normal day so lists always read the same way.
KNOWN_SHIFTS = ["morning", "afternoon", "evening", "weekend"]

# The official source of the real (public university) rows.
PUBLIC_SOURCE = "MOEYS Cambodia - MOEYS_KH__15.08.2017.pdf"
PUBLIC_SOURCE_YEAR = "2017 (file updated 02/07/2018)"

# ---------------------------------------------------------------------------
# Small cleaning helpers
# ---------------------------------------------------------------------------

# The source data writes one province in Khmer. Make it match the others.
PROVINCE_FIXES = {
    "ភ្នំពេញ": "Phnom Penh",  # Phnom Penh in Khmer
}

# Spelling mistakes that exist in the official file. We fix them only so that
# search and filters work; we never change a university's real name.
TYPO_FIXES = {
    "Facutly": "Faculty",
    "Mathamatics": "Mathematics",
    "Manangment": "Management",
    "Langauge": "Language",
    "Institue": "Institute",
    "Architecturs": "Architecture",
}

# A faculty list is usually separated by ";" but sometimes by "," right before
# the next "Faculty of ...". This pattern splits on both cases safely.
FACULTY_SPLIT = re.compile(
    r"\s*;\s*|\s*,\s*(?=(?:Faculty|Department|College|Institute|School)\b)"
)


def _text(value) -> str:
    """Turn any cell into a clean string. Missing values become an empty string."""
    if value is None:
        return ""
    # pandas uses NaN / NA for missing cells.
    if isinstance(value, (list, tuple, set, dict)):
        return str(value)
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value).strip()


def _fix_typos(text: str) -> str:
    """Replace the known spelling mistakes from the official file."""
    for wrong, right in TYPO_FIXES.items():
        text = text.replace(wrong, right)
    return text


def _clean_province(name) -> str:
    """Make province names consistent (Khmer -> English, extra spaces removed)."""
    name = _text(name)
    return PROVINCE_FIXES.get(name, name)


def _make_id(name: str) -> str:
    """Build a short, stable id from a university name."""
    slug = re.sub(r"[^a-z0-9]+", "-", _text(name).lower()).strip("-")
    # Keep ids short, and never end with a dash.
    return slug[:60].strip("-")


def _clean_major(faculty: str) -> str:
    """
    Turn a faculty name into a shorter 'major' name.
    'Faculty of Information Technology' -> 'Information Technology'
    """
    major = _fix_typos(_text(faculty))
    major = re.sub(
        r"^(Faculty|Department|College|Institute|School)\s+of\s+", "", major, flags=re.I
    )
    return major.strip(" .,;")


def _split_faculties(faculty_text) -> list:
    """Split one long faculty string into a clean list of major names."""
    text = _fix_typos(_text(faculty_text))
    if not text:
        return []
    parts = [_clean_major(p) for p in FACULTY_SPLIT.split(text)]
    # Remove empties and duplicates, but keep the original order.
    seen = set()
    result = []
    for p in parts:
        key = p.lower()
        if p and key not in seen:
            seen.add(key)
            result.append(p)
    return result


def _join_address(village, commune, district, province) -> str:
    """Build one readable address line from the separate location columns."""
    parts = [_text(village), _text(commune), _text(district), _clean_province(province)]
    return ", ".join(p for p in parts if p)


# ---------------------------------------------------------------------------
# Reading the raw files
# ---------------------------------------------------------------------------

KML_NS = "{http://www.opengis.net/kml/2.2}"


def _read_kml_coordinates(path: Path) -> pd.DataFrame:
    """
    Read longitude and latitude out of the KML file.
    Returns a small table with: map_id, longitude, latitude.
    """
    rows = []
    for placemark in ET.parse(path).getroot().iter(KML_NS + "Placemark"):
        fields = {sd.get("name"): sd.text for sd in placemark.iter(KML_NS + "SimpleData")}
        point = placemark.find(".//" + KML_NS + "coordinates")
        if point is None or not point.text:
            continue
        lon, lat = point.text.split(",")[:2]
        rows.append(
            {
                "map_id": _text(fields.get("map_id")),
                "longitude": float(lon),
                "latitude": float(lat),
            }
        )
    return pd.DataFrame(rows)


def _load_public_universities() -> pd.DataFrame:
    """Load the 29 real public universities (CSV for details, KML for the map)."""
    csv = pd.read_csv(PUBLIC_CSV, dtype=str)
    coords = _read_kml_coordinates(PUBLIC_KML)

    csv["map_id"] = csv["map_id"].map(_text)
    table = csv.merge(coords, on="map_id", how="left")

    rows = []
    for _, r in table.iterrows():
        name = _text(r["university_name"])
        rows.append(
            {
                "id": _make_id(name),
                "name": name,
                # The MOEYS file we have is the English edition, so there is no
                # Khmer name in it. We keep the column so the pages can show a
                # Khmer name as soon as we find a file that has one.
                "name_kh": "",
                "type": "Public",
                "province": _clean_province(r["province"]),
                "village": _text(r["village"]),
                "commune": _text(r["commune"]),
                "district": _text(r["district"]),
                "address": _join_address(
                    r["village"], r["commune"], r["district"], r["province"]
                ),
                "website": _text(r["website"]),
                "email": _text(r["email"]),
                "tel": _text(r["tel"]),
                # The column name in the CSV really does contain a space.
                "established_year": _text(r["establish _date"]),
                "rector": _text(r["rector"]),
                "faculties_raw": _fix_typos(_text(r["faculty_kh"])),
                "majors": _split_faculties(r["faculty_kh"]),
                "latitude": r["latitude"],
                "longitude": r["longitude"],
                "source": PUBLIC_SOURCE,
                "source_year": PUBLIC_SOURCE_YEAR,
                "last_update": _text(r["last_update"]),
                "is_sample": False,
            }
        )
    return pd.DataFrame(rows)


def _load_sample_private_universities() -> pd.DataFrame:
    """Load the INVENTED private universities used to test the interface."""
    if not PRIVATE_SAMPLE_CSV.exists():
        return pd.DataFrame()

    csv = pd.read_csv(PRIVATE_SAMPLE_CSV, dtype=str)
    rows = []
    for _, r in csv.iterrows():
        rows.append(
            {
                "id": _text(r["id"]),
                "name": _text(r["university_name"]),
                "name_kh": "",
                "type": _text(r["type"]),
                "province": _clean_province(r["province"]),
                "village": _text(r["village"]),
                "commune": _text(r["commune"]),
                "district": _text(r["district"]),
                "address": _join_address(
                    r["village"], r["commune"], r["district"], r["province"]
                ),
                "website": _text(r["website"]),
                "email": _text(r["email"]),
                "tel": _text(r["tel"]),
                "established_year": _text(r["established_year"]),
                "rector": _text(r["rector"]),
                "faculties_raw": _text(r["faculties"]),
                "majors": _split_faculties(r["faculties"]),
                "latitude": float(r["latitude"]),
                "longitude": float(r["longitude"]),
                "source": _text(r["source"]),
                "source_year": "Not real data",
                "last_update": "",
                "is_sample": True,
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# PUBLIC FUNCTIONS - the pages use only these
# ---------------------------------------------------------------------------


def missing_data_files() -> list:
    """
    Return the names of the required data files that are not on disk.
    An empty list means everything we need is there. The pages call this
    first so they can show a friendly message instead of crashing.
    """
    missing = []
    for path in (PUBLIC_CSV, PUBLIC_KML):
        if not path.exists():
            missing.append(path.name)
    return missing


@st.cache_data
def load_universities() -> pd.DataFrame:
    """
    Return one table with every university we know about.

    Columns: id, name, type, province, address, website, email, tel,
             established_year, rector, faculties_raw, majors (list),
             latitude, longitude, source, source_year, last_update, is_sample
    """
    public = _load_public_universities()
    private = _load_sample_private_universities()
    both = pd.concat([public, private], ignore_index=True)
    return both.sort_values("name").reset_index(drop=True)


@st.cache_data
def load_majors() -> pd.DataFrame:
    """
    Return one row per university + major ("long" format).

    Columns: university_id, university_name, type, province, major,
             degree_level, annual_tuition_usd (may be empty), source, is_sample

    For the real public universities we only know the faculty names, so
    annual_tuition_usd is empty. We never invent a fee.
    """
    universities = load_universities()

    rows = []
    for _, u in universities.iterrows():
        if u["is_sample"]:
            continue  # sample fees are loaded from the sample file below
        for major in u["majors"]:
            rows.append(
                {
                    "university_id": u["id"],
                    "university_name": u["name"],
                    "type": u["type"],
                    "province": u["province"],
                    "major": major,
                    "degree_level": "Not published",
                    "annual_tuition_usd": pd.NA,
                    "source": u["source"],
                    "is_sample": False,
                }
            )

    public_majors = pd.DataFrame(rows)

    # Add the sample majors + fees (private universities only).
    if MAJORS_SAMPLE_CSV.exists():
        sample = pd.read_csv(MAJORS_SAMPLE_CSV, dtype=str)
        lookup = universities.set_index("id")
        sample_rows = []
        for _, r in sample.iterrows():
            uid = _text(r["university_id"])
            if uid not in lookup.index:
                continue
            sample_rows.append(
                {
                    "university_id": uid,
                    "university_name": _text(r["university_name"]),
                    "type": lookup.loc[uid, "type"],
                    "province": lookup.loc[uid, "province"],
                    "major": _text(r["major"]),
                    "degree_level": _text(r["degree_level"]),
                    "annual_tuition_usd": pd.to_numeric(
                        r["annual_tuition_usd"], errors="coerce"
                    ),
                    "source": _text(r["source"]),
                    "is_sample": True,
                }
            )
        sample_majors = pd.DataFrame(sample_rows)
        all_majors = pd.concat([public_majors, sample_majors], ignore_index=True)
    else:
        all_majors = public_majors

    all_majors["annual_tuition_usd"] = pd.to_numeric(
        all_majors["annual_tuition_usd"], errors="coerce"
    )
    return all_majors


@st.cache_data
def load_study_shifts() -> dict:
    """
    Read data/collected/study_shifts.csv and return what we know about study
    times, as {university_id: {"shifts": [...], "source": str, "checked_on": str}}.

    A university is in this dictionary ONLY if someone actually checked it and
    wrote the shifts in the file. Everything else is simply absent, which the
    rest of the app reads as "we do not know" - never as "no evening classes".

    The file is optional: if it is missing the app still works, it just has no
    shift information at all.
    """
    if not SHIFTS_CSV.exists():
        return {}

    table = pd.read_csv(SHIFTS_CSV, dtype=str).fillna("")

    known = {}
    for _, row in table.iterrows():
        university_id = _text(row.get("university_id"))
        raw_shifts = _text(row.get("shifts"))

        # An empty "shifts" cell means nobody has checked this university yet.
        if not university_id or not raw_shifts:
            continue

        # "morning;evening" -> ["morning", "evening"], keeping the day order
        # and quietly dropping anything that is not one of the four words.
        written = [part.strip().lower() for part in raw_shifts.split(";")]
        shifts = [shift for shift in KNOWN_SHIFTS if shift in written]
        if not shifts:
            continue

        known[university_id] = {
            "shifts": shifts,
            "source": _text(row.get("source")),
            "checked_on": _text(row.get("checked_on")),
        }

    return known


def get_shifts(university_id: str) -> dict:
    """
    What we know about one university's study times.

    Always returns a dictionary, so a page never has to check for None:
        {"known": False, "shifts": [], "source": "", "checked_on": ""}
    """
    found = load_study_shifts().get(university_id)
    if not found:
        return {"known": False, "shifts": [], "source": "", "checked_on": ""}

    return {"known": True, **found}


def format_shifts(university_id: str) -> str:
    """
    A ready-to-print line about study times, e.g. "Morning, Evening".

    Returns SHIFT_NOT_PUBLISHED when nobody has checked this university yet.
    """
    info = get_shifts(university_id)
    if not info["known"]:
        return SHIFT_NOT_PUBLISHED

    return ", ".join(shift.capitalize() for shift in info["shifts"])


@st.cache_data
def list_provinces() -> list:
    """Every province that has at least one university, sorted A-Z."""
    provinces = load_universities()["province"]
    return sorted(p for p in provinces.unique() if p)


@st.cache_data
def list_majors() -> list:
    """Every major (faculty) name we know, sorted A-Z, no duplicates."""
    majors = load_majors()["major"]
    return sorted(m for m in majors.unique() if m)


@st.cache_data
def list_types() -> list:
    """The university types available: Public and/or Private."""
    return sorted(t for t in load_universities()["type"].unique() if t)


def get_university(university_id: str) -> dict:
    """Return one university as a plain dictionary, or None if the id is unknown."""
    table = load_universities()
    match = table[table["id"] == university_id]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def get_universities_by_ids(university_ids: list) -> pd.DataFrame:
    """Return the rows for a list of ids (used by Compare and My Favorites)."""
    table = load_universities()
    return table[table["id"].isin(university_ids)].reset_index(drop=True)


def get_majors_for(university_id: str) -> pd.DataFrame:
    """Return the majors (and fees, when known) of one university."""
    majors = load_majors()
    return majors[majors["university_id"] == university_id].reset_index(drop=True)


def get_tuition_range(university_id: str):
    """
    Return (lowest fee, highest fee) in USD for one university.
    Returns (None, None) when no fee is published. We never guess.
    """
    fees = get_majors_for(university_id)["annual_tuition_usd"].dropna()
    if fees.empty:
        return (None, None)
    return (float(fees.min()), float(fees.max()))


def format_tuition(university_id: str) -> str:
    """Return a ready-to-show fee text, e.g. '$450 - $1,500' or 'Fee not published'."""
    low, high = get_tuition_range(university_id)
    if low is None:
        return FEE_NOT_PUBLISHED
    if low == high:
        return f"${low:,.0f}"
    return f"${low:,.0f} - ${high:,.0f}"


def search_universities(
    name_query: str = "",
    types: list = None,
    provinces: list = None,
    majors: list = None,
) -> pd.DataFrame:
    """
    Filter the university table for the Browse page.

    Every argument is optional. An empty or None argument means "do not filter".
    """
    table = load_universities()

    # Filter by name (not case sensitive).
    query = _text(name_query).lower()
    if query:
        table = table[table["name"].str.lower().str.contains(query, na=False)]

    # Filter by type (Public / Private).
    if types:
        table = table[table["type"].isin(types)]

    # Filter by province.
    if provinces:
        table = table[table["province"].isin(provinces)]

    # Filter by major: keep a university if it offers ANY of the chosen majors.
    if majors:
        wanted = {m.lower() for m in majors}
        keep = table["majors"].map(
            lambda offered: any(m.lower() in wanted for m in offered)
        )
        table = table[keep]

    return table.reset_index(drop=True)


@st.cache_data
def get_summary_stats() -> dict:
    """The key numbers shown on the Home page."""
    table = load_universities()
    return {
        "total": len(table),
        "public": int((table["type"] == "Public").sum()),
        "private": int((table["type"] == "Private").sum()),
        "provinces": table["province"].nunique(),
        "majors": len(list_majors()),
        "sample_rows": int(table["is_sample"].sum()),
        "real_rows": int((~table["is_sample"]).sum()),
    }

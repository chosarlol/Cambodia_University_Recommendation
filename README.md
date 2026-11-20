# Cambodia University Recommendation

A web application that helps Cambodian high school graduates find a public or
private university that matches their **major**, **province** and **budget**.

Course project for *Web Application Development for Data Science*,
Year 3 Data Science, Royal University of Phnom Penh.

**Current scope: frontend only (Streamlit).** There is no backend, no database
and no login yet. All data is read from files through `services/data.py`, so the
same functions can later call a FastAPI backend instead.

> **Continuing the project?** Read [Latest changes (20 Nov 2026)](#latest-changes-20-nov-2026)
> and [Next steps](#next-steps) at the bottom first.

---

## How to run the app

```bash
# 1. Go to the project folder
cd project-WAD

# 2. Create a virtual environment (only the first time)
python -m venv .venv

# 3. Activate it
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

# 4. Install the libraries (only the first time)
pip install -r requirements.txt

# 5. Start the app
python -m streamlit run app.py
```

> If PowerShell says *"streamlit is not recognized"*, the Python Scripts folder
> is not on your PATH. `python -m streamlit run app.py` always works.

Editing a CSV in `data/` while the app runs is fine: the page shows the new
data on the next refresh (see [Caching](#caching)). After editing **code**,
Streamlit usually reloads by itself; restart it (Ctrl + C, then run again) if a
page shows an old error.

The app opens in your browser at <http://localhost:8501>.

### On Windows, check which `python` you are using

On the machine this project was built on, the bare `python` on the PATH is
**msys2 and has no pandas**, so a virtual environment created with it cannot
run the app. Build the venv from a full Python instead (here, Anaconda's
Python 3.13):

```bash
"C:\ProgramData\anaconda3\python.exe" -m venv .venv
```

The most reliable way to start the app is to call the venv's interpreter
directly, without relying on an activated shell:

```bash
.venv/Scripts/python.exe -m streamlit run app.py
```

> **Streamlit 1.46 or newer is recommended.** The top navigation bar uses
> `st.navigation(position="top")`. On an older version the app still runs, but
> the navigation falls back to the sidebar (see `build_navigation()` in
> `app.py`).

`plotly`, `folium` and `streamlit-folium` are listed in `requirements.txt` but
are not used yet - they are installed ahead of the Map step.

---

## The pages

| Page | File | What it does |
|---|---|---|
| Home | `app.py` (`render_home`) | Hero banner with a photo slideshow (RULE, RUPP, RUFA - changes every 10 s; the university name bottom right opens its page), search box, the two paths, quick form, key numbers, how it works |
| Find My University | `pages/recommend.py` | The same form with more room and a short explanation |
| Results | `pages/results.py` | The visitor's matches. **Ranking not built yet** - currently a filtered list |
| Explore | `pages/browse.py` | Every university in one table, with filters, search and favorites. **Tick one or more rows, then press the blue "Open selected universities" button** |
| University (`/university`) | `pages/detail.py` | One university in full: Khmer name, address, contact, fee range, majors table (Khmer name, faculty, level, fee, entrance exam, shifts, places, notes), data source. **Several ticked universities = one tab each** |
| Compare | `pages/compare.py` | 2-3 universities side by side (basic facts for now) |
| Favorites | `pages/favorites.py` | The universities the visitor saved |
| About | `pages/about.py` | Data sources and the warnings about them |

The Detail page is reached by clicking a university name (Home banner, Explore
cards, Results, Favorites) or by ticking rows on Explore. It still appears in
the navigation list, because `st.switch_page()` only works for pages that are
part of it. Its web address is **`/university`**. The chosen ids travel in
`st.session_state` and in the address - one university `?uni=id`, several
`?uni=id-one,id-two` - so the page can be refreshed or the link shared.

---

## Project structure

```
project-WAD/
├── app.py                      # entry point, top navigation and Home page
├── assets/
│   ├── logo.svg                # site logo shown in the top bar
│   └── hero/                   # Home slideshow photos: rule.jpg, rupp.jpg, rufa.jpg
├── pages/
│   ├── recommend.py            # Find My University (the full form)
│   ├── results.py              # ranked results
│   ├── browse.py               # Explore universities (filters + search)
│   ├── detail.py               # one university in full
│   ├── compare.py              # side-by-side comparison
│   ├── favorites.py            # saved universities
│   └── about.py                # data sources and warnings
├── services/
│   ├── __init__.py
│   └── data.py                 # ALL data loading and cleaning
├── utils/
│   ├── __init__.py
│   ├── forms.py                # the recommendation form (shared by 2 pages)
│   ├── state.py                # st.session_state keys in one place
│   ├── style.py                # all custom CSS and the footer
│   └── validation.py           # form validation helpers
├── data/
│   ├── raw/                    # real data from the Ministry of Education
│   ├── collected/              # study shifts, checked by our team
│   └── major_detail/           # majors, fees, Khmer names - one CSV per university (29)
│       ├── README.md           # column guide, progress table, corrections made
│       └── source_files/       # the original Excel / Word / screenshot files we received
├── .streamlit/config.toml      # theme
├── requirements.txt
└── .gitignore
```

### Why `services/data.py` matters

Pages never open a CSV or KML file themselves. They call functions such as
`data.load_universities()` or `data.search_universities(...)`. When the backend
is added later, only the inside of those functions changes - every page keeps
working.

The functions a page is allowed to call:

| Function | Returns |
|---|---|
| `missing_data_files()` | List of expected data files that are not on disk |
| `load_universities()` | One row per university (29 public), incl. `name_kh` and `detail_notes` |
| `load_majors()` | One row per university-major pair, with fees, Khmer name, faculty, level, entrance exam, shifts, places, notes |
| `list_provinces()`, `list_majors()`, `list_types()` | The dropdown options |
| `get_university(id)` | One university as a dict, or `None` |
| `get_universities_by_ids(ids)` | Those universities as a DataFrame |
| `get_majors_for(id)` | That university's majors and fees |
| `get_tuition_range(id)` | The low and high yearly fee in USD, or `None` |
| `format_tuition(id)` | A ready-to-print fee string, or `FEE_NOT_PUBLISHED` (use inside tables) |
| `format_tuition_markdown(id)` | The same with `$` escaped - use in `st.write` / `st.caption` / `st.metric`, where Streamlit would otherwise read `$300 - $2,500` as a math formula |
| `get_fee_sources(id)` | Where that university's fees came from |
| `get_shifts(id)`, `format_shifts(id)` | Study shifts from `data/collected/study_shifts.csv` |
| `get_collection_progress()` | How many universities have majors / fees (used on the About page) |
| `search_universities(types, provinces, majors, ...)` | The filtered list |
| `get_summary_stats()` | The counts shown on the Home page |

### Caching

The loaders are cached with `@st.cache_data`, so files are not read on every
click. The cache key includes the modification time of **every file in
`data/` and of `services/data.py`** (`_data_version()`), so editing a CSV or the
loader is picked up on the next page refresh. Without this the app kept
showing old data (e.g. ITC without fees) until it was restarted.

---

## Where the data comes from

### Real data (`data/raw/`)

| File | Content |
|---|---|
| `public-university-of-cambodia-english-language.csv` | 29 public universities: name, contact, location, faculties |
| `public_universities.kml` | The same 29 universities with longitude / latitude |
| `PublicUniversitiesinCambodia2021(KML).kml` | A newer 2021 list - **kept for reference, not used** (see below) |
| `moeys_kh__15.08.2017.pdf` | The original Ministry document |

**Source:** Ministry of Education, Youth and Sport (MOEYS), Cambodia.
Document `MOEYS_KH__15.08.2017.pdf`, data file last updated **02/07/2018**.

All 29 real universities have longitude and latitude from the KML, so the map
step has complete coordinates. Two of the 29 have no website at all.

#### Why the 2021 file is not used

The 2021 KML file is damaged. Its field names are shifted by two positions, the
**university name and website columns were saved as `0` for all 37 rows**, and
6 rows have a different number of fields so the shift is not the same
everywhere. Matching on email domain recovered only 26 of the 37 names.
Rather than guess the missing names, the project uses the complete and reliable
2018 dataset.

### Collected by our team (`data/collected/`, `data/major_detail/`)

The Ministry data has **no tuition fees** and only broad faculty names.
`data/major_detail/` holds **one CSV per university** (`<university_id>.csv`)
with the real majors, their Khmer names and, where we found them, yearly fees.
When a university has a file there, **its majors replace the MOEYS faculty
list** in the app. Column guide and progress: `data/major_detail/README.md`.

- All **29** universities have their majors (343 majors, 247 distinct names).
- Fees are known for **11**: RUPP, ITC, NPIC, NTTI, PPI, RUFA, UHS (both
  campuses), NIPTICT, UHST, RULE.
- Fees in riel (RUPP) are converted at **4,100 riel = 1 USD** (`KHR_PER_USD`).
- A fee that is a range (e.g. ITC $450 - $600 by year of study) uses
  `annual_tuition_usd` (lowest) + `annual_tuition_usd_max` (highest).
- Entrance exam subjects, places and shifts per major exist **for RUPP only**.

`data/collected/study_shifts.csv` holds the study shifts per university (see
`data/collected/README_COLLECTED.md`).

#### Renamed universities

The app id is always built from the 2017 MOEYS name, so links, favorites and
`study_shifts.csv` keep working. The name shown on the site is set in
`NAME_FIXES` in `services/data.py`:

| App id | Shown as |
|---|---|
| `mean-chey-university` | National Meanchey University (NMU) |
| `university-of-battambang` | National University of Battambang (NUBB) |
| `chea-sim-university-of-kamchaymear-formerly-maharishi-vedic` | National University of Chea Sim Kamchaymear (NUCK) |

---

## Known limits of the data

- **Fees are known for 11 universities** (RUPP, ITC, NPIC, NTTI, PPI, RUFA,
  UHS both campuses, NIPTICT, UHST, RULE). The others show *"Fee not published"* -
  the app never guesses.
- **No private universities yet.** The Ministry data has none and we have not
  collected any, so the site lists the 29 public universities only.
- **247 distinct major names** in the Major filter, often the same subject
  written differently (e.g. "Accountancy" / "Accounting"). Grouping them into
  subject areas would make the filter and the ranking much easier.
- **Subject requirements are almost empty.** Only RUPP has entrance exam
  subjects; no university has BacII stream or grade requirements yet.
- **Khmer university names missing** for RUPP and NIPTICT. NMU's Khmer name in
  our file is the old one (សាកលវិទ្យាល័យមានជ័យ).
- **Sources are placeholders.** Every collected row says
  "Collected by our team - <file>" and `checked_on` is empty.
- **Two universities have no website**, so the Detail page shows a disabled
  "Website not published" button rather than a dead link.
- The data is from 2017/2018. **Students must confirm every detail with the
  university before applying.**

### Cleaning applied in `services/data.py`

1. One province written in Khmer is converted to `Phnom Penh`.
2. Spelling mistakes in the official file are corrected for search only
   (`Facutly`, `Mathamatics`, `Manangment`, `Langauge`, `Institue`, `Architecturs`).
3. Faculty lists are split on `;` and on `,` when it is followed by
   `Faculty`/`Department`/`College`/`Institute`/`School`.
4. `Faculty of ...` prefixes are removed to get a shorter major name.
5. Village, commune, district and province are joined into one address line.
6. The column `establish _date` (which contains a space) is renamed
   `established_year`.

---

## Build progress

- [x] Step 0 - inspect the data
- [x] Data layer (`services/data.py`)
- [x] Majors collected for all 29 universities, fees for 11 (`data/major_detail/`)
- [x] Home page, top navigation, custom theme
- [x] Explore / Browse with filters, search and favorites
- [x] Recommendation form + validation (`utils/forms.py`, `utils/validation.py`)
- [x] University Detail page (address, contact, fee, majors, source)
- [x] Compare page - basic facts side by side
- [x] Home hero slideshow with clickable university names
- [x] Explore: tick several universities and open them together (one tab each)
- [x] Sample (invented) private universities removed - real data only
- [ ] **Ranking function (`services/recommend.py`) - match score and reasons**
- [ ] Results page: show the score and the reasons instead of a filtered list
- [ ] Compare page: the full table (every field, all majors)
- [ ] Map of university locations (the coordinates are already loaded)

### How a visitor moves through the site

**Path A - "Recommend for me":** Home -> quick form -> Results (ranked list)
**Path B - "I'll explore myself":** Home -> search box or Explore -> filter -> Favorites

From either path, clicking a university name opens its Detail page, and from
there the visitor can save it to Favorites or send it to Compare.

Both paths keep their state in `st.session_state` (see `utils/state.py`), so
nothing the visitor typed is lost when they change page. What is kept: the
visitor's `profile` from the form, their `favorites`, the universities queued
for `compare`, the `search_text`, and the university currently opened.

---

## Latest changes (20 Nov 2026)

1. **Majors and fees for all 29 universities** - `data/major_detail/`, one CSV
   per university, built from the group's Excel / Word files (originals in
   `source_files/`). The RUPP translation was corrected (Faculty of
   Engineering, Information Technology Engineering, Mechanical Engineering,
   The Department of Media and Communication) - listed in that folder's README.
2. **Loader** (`services/data.py`): `_read_collected_majors()` reads the
   folder; Khmer names, fee ranges, riel conversion, university notes;
   `NAME_FIXES` for renamed universities; the cache refreshes when files change.
3. **University page**: majors table with every column we have (empty columns
   are hidden), faculty filter, university notes (discounts, BacII-grade fees),
   sources; several universities shown as tabs.
4. **Explore**: multi-row ticking + blue "Open selected universities" button.
5. **Home**: photo slideshow (`HERO_SLIDES` / `HERO_SECONDS` in `app.py`,
   styles in `utils/style.py`). The name buttons are real Streamlit buttons,
   so favorites are kept when one is clicked.
6. **`$` bug fixed**: fee ranges like `$300 - $2,500` were shown as
   `300 - 2,500` (Streamlit math). Use `format_tuition_markdown()` in text.
7. **Sample data removed**: `data/sample/` and all "SAMPLE" code and wording.
   The Public / Private / Either choice was kept for when private
   universities are added.
8. **About page** counts the collected universities from the data, so it stays
   correct as files are added.

## Next steps

- [ ] **Ranking** (`services/recommend.py`): match score + reasons, then show
  them on the Results page. The fee range, major list and shifts are ready to
  use; `get_tuition_range(id)` gives the numbers for the budget check.
- [ ] **Fees for the 18 universities without any**: CMI, HSI, ITI, IES, KNIA,
  KCIT, KSIT, NIB, NMU, NUBB, NUCK, NUM, PSRBU, PNCA, RUA, SRU, UEF, UKT.
  Fill `annual_tuition_usd` (+ `annual_tuition_usd_max` for a range) in their
  CSV - no code change needed.
- [ ] **Subject requirements**: fill `entrance_exam` (and maybe add a BacII
  stream column) for more universities.
- [ ] Group the 247 major names into subject areas for the filter.
- [ ] Real sources + `checked_on` dates instead of "Collected by our team".
- [ ] Check the Khmer typed in from the UEF screenshot.
- [ ] Missing Khmer names: RUPP, NIPTICT; new Khmer name for NMU.
- [ ] Compare page: full table; Map page (coordinates already loaded).
- [ ] Private universities (none yet).

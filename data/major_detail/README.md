# Major detail - majors, fees and subjects per university

Real data collected by our team. The Ministry (MOEYS) file only lists broad
faculties ("Faculty of Science") and has **no fees**. This folder fills that gap.

- **One CSV per university**, named `<university_id>.csv`. The id is the one
  the app uses (see `data/collected/study_shifts.csv` for the full list).
- When a university has a file here, **its majors replace the MOEYS faculty
  list** in the app.
- `source_files/` keeps the original Excel / Word files we received, so every
  CSV can be checked against where it came from.

The loader is `_read_collected_majors()` in `services/data.py`. It reads every
`*.csv` in this folder, so adding a university = adding one file.

## Columns

| Column | What to write |
|---|---|
| `university_id` | The app id, e.g. `royal-university-of-phnom-penh`. **Must match exactly.** |
| `university_name` | English name, to make the file readable |
| `university_name_kh` | Khmer name of the university (shown on the site) |
| `faculty` | e.g. `Faculty of Science`. Optional |
| `major` | English major name. **Required** |
| `major_kh` | Khmer major name. Optional |
| `degree_level` | e.g. `Bachelor (4 Years)`. Optional |
| `fee_khr` | Yearly fee in riel, if the university gives riel |
| `annual_tuition_usd` | Yearly fee in USD. If the fee is a range, the **lowest** value. Empty + `fee_khr` filled = converted at 4,100 riel = 1 USD |
| `annual_tuition_usd_max` | The **highest** value when the fee is a range (e.g. ITC $450 - $600). Empty otherwise |
| `entrance_exam` | Entrance exam subject(s), as written by the university |
| `places_morning` / `places_afternoon` / `places_evening` | Places per shift. Empty = shift not offered |
| `places_total` | Total places |
| `source` | Where the data came from. **Rows with an empty source are ignored.** |
| `checked_on` | Date checked, `YYYY-MM-DD` |
| `notes` | Note for this major (e.g. fee per year of study) |
| `university_note` | Note for the whole university (discounts, scholarships). Shown once on the Detail page |

Save the files as **CSV UTF-8** so the Khmer text is kept. Excel: *File > Save
As > CSV UTF-8 (Comma delimited)*.

## Progress (all 29 public universities)

| File | Majors | Fees | Original file |
|---|---|---|---|
| `royal-university-of-phnom-penh.csv` | 41 | Yes (riel) | `RUPP_Khmer_program_table_translation.docx` |
| `institute-of-technology-of-cambodia.csv` | 7 | Yes (range) | `ITC_Majors_and_Fees.xlsx` |
| `national-polytechnic-institute-of-cambodia.csv` | 9 | Yes | `NPIC_Majors_and_Fees.xlsx` |
| `national-technical-training-institute.csv` | 5 | Yes (range) | `NTTI_Majors_and_Fees.xlsx` |
| `preah-kossomak-polytechnic-institute.csv` | 8 | Yes | `PPI_Majors_and_Fees.xlsx` |
| `royal-university-of-fine-arts.csv` | 15 | Yes (range) | `RUFA_Majors_and_Fees.xlsx` |
| `cambodia-maritime-institute.csv` | 2 | No | `CMI_Majors.xlsx` |
| `health-science-institute-of-r-c-a-f.csv` | 10 | No | `HSI_RCAF_Majors.xlsx` |
| `institute-of-electrical-science.csv` | 4 | No | `IES_Majors.xlsx` |
| `industrial-technical-institute.csv` | 4 | No | `ITI_Majors.xlsx` |
| `kampong-chheuteal-institute-of-technology.csv` | 8 | No | `KCIT_Majors.xlsx` |
| `kampong-cham-national-school-of-agriculture.csv` | 9 | No | `KNIA_Majors.xlsx` (now called Kampong Cham National Institute of Agriculture) |
| `kampong-speu-institute-of-technology.csv` | 10 | No | `KSIT_Majors.xlsx` |
| `national-institute-of-business.csv` | 14 | No | `NIB_Majors-v2.xlsx` |
| `university-of-kratie.csv` | 12 | No | `UKT_Majors.xlsx` |
| `university-of-health-sciences-cambodia-first-campus.csv` | 8 | Yes | `UHS_Campus1_Majors_and_Fees.xlsx` |
| `university-of-health-sciences-second-campus.csv` | 7 | Yes | `UHS_Campus2_Majors_and_Fees.xlsx` |
| `national-institue-of-posts-telecommunications-and-informatio.csv` | 3 | Yes | `NIPTICT_Majors_and_Fees.xlsx` (NIPTICT / CADT) |
| `university-of-heng-samrin-thbongkhmum.csv` | 22 | Yes (by year and BacII grade) | `UHST_Majors_and_Fees.xlsx` |
| `mean-chey-university.csv` | 15 | No | `MCU_Majors.xlsx` - shown as **National Meanchey University (NMU)** |
| `university-of-battambang.csv` | 23 | No | `NUBB_Majors.xlsx` - shown as **National University of Battambang (NUBB)** |
| `preah-sihanouk-raja-buddhist-university.csv` | 8 | No | `PSRBU_Majors.xlsx` |
| `royal-university-of-law-and-economics.csv` | 18 | Yes | `RULE_Majors_and_Fees.xlsx` |
| `chea-sim-university-of-kamchaymear-formerly-maharishi-vedic.csv` | 16 | No | `NUCK_Majors.xlsx` - shown as **National University of Chea Sim Kamchaymear (NUCK)** |
| `national-university-of-management.csv` | 19 | No | `NUM_Majors.xlsx` |
| `prek-leap-national-college-of-agriculture.csv` | 7 | No | `PNCA_Majors.xlsx` |
| `royal-university-of-agriculture.csv` | 14 | No | `RUA_Majors.xlsx` |
| `svay-rieng-university.csv` | 21 | No | `SRU_Majors.xlsx` |
| `university-of-economics-and-finance.csv` | 4 | No | `UEF_Majors_screenshot.png` (typed in from a screenshot - please check the Khmer) |

### Still to collect

Every university now has its majors. Fees are still missing for 18 of them.

### Renamed universities

The app id always comes from the 2017 MOEYS name, so links keep working. The
name shown on the site can be changed in `NAME_FIXES` in `services/data.py`:

- `mean-chey-university` is shown as **National Meanchey University (NMU)**.
- `university-of-battambang` is shown as **National University of Battambang (NUBB)**.
- `chea-sim-university-of-kamchaymear-formerly-maharishi-vedic` is shown as
  **National University of Chea Sim Kamchaymear (NUCK)**.

### Before the presentation

- `source` currently says "Collected by our team - <file>". Replace it with
  the real source (website link, brochure, phone call) and fill `checked_on`.
- RUPP and NIPTICT: the Khmer university name is empty (their files did not
  include it). RUPP: the academic year of the fee table is not stated.
- NMU: the Khmer name in `MCU_Majors.xlsx` is the old one (សាកលវិទ្យាល័យមានជ័យ).

### Corrections made to the RUPP translation

The CSV differs from `RUPP_Khmer_program_table_translation.docx` here (the
Word file is kept unchanged as the original):

- Section D is the **Faculty of Engineering** (the translation said
  "Faculty of Agriculture").
- D3 is **Information Technology Engineering** (was "Information technology
  and engineering").
- D8 is **Mechanical Engineering** (was "Agricultural Mechanics").
- A8 is **The Department of Media and Communication** (was "Mass Media and
  Communication").

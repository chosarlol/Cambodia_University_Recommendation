# Collected data - real, but gathered by us

This folder is **not** from the Ministry, and it is **not** invented sample
data. It is information we checked ourselves, one university at a time, with
the source written next to every value.

## `study_shifts.csv`

When you can study: morning, afternoon, evening or weekend. This matters
because many Cambodian students work during the day, and a university that
only teaches in the morning is impossible for them.

The MOEYS file has 17 columns and **none of them mentions study times**, so
there was nothing to clean or reuse - the data has to be collected.

### Columns

| Column | What to write |
|---|---|
| `university_id` | Already filled in. Do not change it - the app matches on it. |
| `university_name` | Already filled in, to make the file readable. |
| `shifts` | The shifts, separated by `;` - for example `morning;evening` |
| `source` | Where you saw it: a URL, a Facebook post, or "phoned the office" |
| `checked_on` | The date you checked, as `YYYY-MM-DD` |
| `notes` | Anything odd, e.g. "evening classes only for year 3 and 4" |

Only these four words are accepted in `shifts`, in any order:

```
morning    afternoon    evening    weekend
```

Anything else is ignored by the loader. The app always prints them in day
order, no matter how you typed them.

### The rule for this file

**An empty `shifts` cell means "we have not checked yet" - it does NOT mean
"no evening classes".** The app treats the two completely differently:

- A university you have filled in and that matches the student's shift gains
  points in the ranking and shows its shifts on the detail page.
- A university you have not checked is **still shown**, never hidden, with a
  note telling the student to ask the university directly.

So leaving a row empty is always safe. Guessing is not: writing `evening` for
a university that does not teach in the evening could send a working student
to apply somewhere they cannot actually attend.

If you cannot confirm a university, leave it empty and move on.

### Progress

29 rows, one per real public university. The Royal University of Phnom Penh
row is filled in as a worked example so the feature can be seen running - its
`source` still says CONFIRM, and it needs a real link before the presentation.

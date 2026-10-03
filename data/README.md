# Backup database

Structured, queryable backup of the marathon plan and training log. `index.html` is the
source of truth for display; these CSVs are the durable data layer. Every `git push` backs
them up offsite to GitHub.

## Files

- **`plan.csv`** — every day of the 21-week plan (one row per day).
  Columns: `phase, week, week_dates, week_target, date, day, workout, type, distance_mi`.
  **Generated** from `index.html` — do not hand-edit. Regenerate after any plan change:
  ```bash
  python3 data/build_plan_csv.py
  ```

- **`log.csv`** — every actual run (one row per run, oldest-first, append-only).
  Columns: `date, day, week, type, prescribed, actual_mi, pace, moving_time, avg_hr, max_hr, elevation_ft, verdict, strava_id, relative_effort, feel, notes, athlete`.
  `relative_effort` = Strava's suffer_score; `feel` = JR's own Strava note (blank if he didn't write one).
  `athlete` = whose run it is (`jr`, or a training partner's roster slug). It is the LAST
  column so the positional queries below keep working.
  **Every tally must filter to `athlete=="jr"`** — partner rows are stored for reference,
  not to be averaged into JR's mileage. Partner rows carry no `verdict`, `prescribed`,
  `week`, or `notes`; they are never written to `training-log.md` or the site's Log tab.
  The Strava auto-ingest (`.claude/commands/log-runs.md`) appends a row per run.

- **`build_plan_csv.py`** — regenerates `plan.csv` from `index.html`.

## Quick queries

```bash
# All long runs in the plan
awk -F, '$8=="Long"' data/plan.csv

# Every one of JR's runs flagged off-plan
#   ($NF is the athlete column — being last, it survives commas inside quoted notes)
awk -F, '$NF=="jr" && $12=="off-plan"' data/log.csv

# JR's total logged mileage (partners excluded)
awk -F, 'NR>1 && $NF=="jr"{s+=$6} END{print s" mi"}' data/log.csv

# Total prescribed mileage
awk -F, 'NR>1{s+=$9} END{print s" mi"}' data/plan.csv
```

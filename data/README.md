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
  Columns: `date, day, week, type, prescribed, actual_mi, pace, moving_time, avg_hr, max_hr, elevation_ft, verdict, strava_id, notes`.
  The Strava auto-ingest (`.claude/commands/log-runs.md`) appends a row per run.

- **`build_plan_csv.py`** — regenerates `plan.csv` from `index.html`.

## Quick queries

```bash
# All long runs in the plan
awk -F, '$8=="Long"' data/plan.csv

# Every run flagged off-plan
awk -F, '$12=="off-plan"' data/log.csv

# Total prescribed mileage
awk -F, 'NR>1{s+=$9} END{print s" mi"}' data/plan.csv
```

---
description: Ingest new Strava activities (filed as GitHub issues) into the training log
---

# /log-runs — Ingest Strava activities into the training log

Strava activities arrive as GitHub issues (Zapier files them, label `strava-activity`).
Process every open one, run the coach verdict against the plan, write it to BOTH places,
commit, push, and close the issue. Act as JR's coach per `CLAUDE.md`, not a generic logger.

## Expected issue body (what Zapier files)

Zapier maps Strava fields into this `key: value` body. Keys are fixed; the routine parses
them literally. Optional keys may be blank or absent.

```
strava_id: {{id}}
name: {{name}}
type: {{type}}
start_date_local: {{start_date_local}}
distance_m: {{distance}}
moving_time_s: {{moving_time}}
elapsed_time_s: {{elapsed_time}}
total_elevation_gain_m: {{total_elevation_gain}}
average_speed_ms: {{average_speed}}
max_speed_ms: {{max_speed}}
average_heartrate: {{average_heartrate}}
max_heartrate: {{max_heartrate}}
average_cadence: {{average_cadence}}
description: {{description}}            # optional → Feel
perceived_exertion: {{perceived_exertion}}  # optional → RPE
relative_effort: {{suffer_score}}     # optional → training load
average_temp: {{average_temp}}        # optional
gear: {{gear_name}}                   # optional → shoe mileage
splits_standard: {{=JSON.stringify(gives[...]["splits_standard"])}}  # optional → per-mile splits as a JSON array
```

`splits_standard`, when present, is a JSON array of per-mile split objects, each with
`distance` (m), `moving_time`/`elapsed_time` (s), `average_speed` (m/s), `average_heartrate`,
`elevation_difference` (m), `split` (mile index). Parse it (steps 3 & 7) to build the
per-mile table. (HR-zone % is still not in the feed; only splits are.) If `splits_standard` is
absent or unparseable, just skip the splits table — the rest of the entry is unaffected.

## Source of truth
- **The plan** lives in `index.html`, **Plan tab** — week tables with one row per day
  (`<td class="dc">Wed Jun 10</td><td>4×1200m @ 7:55/mi …</td>`). Week 1 starts **June 8**.
  Runs dated before June 8 are **pre-season base runs**, not part of a numbered week.
- **The log** lives in TWO files that must stay in sync — write both, every time:
  1. `training-log.md` — long-form journal (full coach notes). Newest at top.
  2. `index.html`, **Training Log tab** (`<table class="log-table">`) — compact row the
     site displays. Newest at top.
  3. `data/log.csv` — structured backup DB, append-only, **oldest at top** (newest row
     appended at the bottom). One row per run.

## Steps

1. **Pull the queue:**
   ```bash
   gh issue list --label strava-activity --state open --json number,title,body --limit 50
   ```
   If empty, stop.

2. **Parse** each issue's `key: value` body. RAW Strava units: `distance_m` (m),
   `moving_time_s`/`elapsed_time_s` (s), `total_elevation_gain_m` (m), `average_speed_ms`
   (m/s), `average_heartrate`, `max_heartrate`, `average_cadence`, `start_date_local`,
   `type`, `strava_id`. **Optional fields (use if present, ignore if blank/missing):**
   `description` (JR's own note → use as **Feel**), `perceived_exertion` (RPE),
   `relative_effort` (Strava suffer_score), `average_temp`, `gear`,
   `splits_standard` (JSON array of per-mile splits).

3. **Convert:** miles = `distance_m`/1609.34 · pace = (`moving_time_s`/60)/miles → `M:SS/mi`
   · elevation ft = `total_elevation_gain_m`×3.28084. Only log `type: Run`; for anything
   else close the issue with "skipped — not a run".
   **Splits:** if `splits_standard` is present, parse the JSON. For each split compute
   per-mile pace = (`moving_time`/60)/(`distance`/1609.34) → `M:SS`, and read its
   `average_heartrate` and `elevation_difference` (×3.28084 → ft). This gives the per-mile
   pace · HR table and, on a quality day, the actual work-rep pace.

4. **Dedupe:** if either log already contains that `strava_id` (stamped as an HTML comment
   in `training-log.md`), skip and close the issue. Never double-log.

5. **Find the prescription.** In `index.html` Plan tab, locate the row for that run's date.
   - Date ≥ Jun 8 → it belongs to a numbered week; use that day's prescribed workout.
   - Date < Jun 8 → pre-season base run; judge against general base guidance, not a week.
   - **The plan file is the source of truth. If a run meets or beats the prescribed
     target, never mark it short.** Only flag genuine misses.

6. **Verdict** per `CLAUDE.md`: right day for the effort (hard/easy principle is critical),
   pace vs the zone, avg HR vs ~190 max (>~75% Z3+ on an easy day = intensity miss),
   distance vs prescribed. Pick ✅ on plan · ⚠️ off plan · 🚩 flag.
   **For quality sessions (intervals/tempo), judge the WORK reps, not the whole-run
   average.** If splits are present, identify the fast/work miles and compare their pace to
   the prescribed rep pace — hitting rep pace ✅ even if total volume is a touch short. Don't
   penalize an interval day for trimmed warm-up/cool-down volume when the reps were on target.

7. **Write `training-log.md`** — new entry at the top of the current section, matching the
   existing format, including `<!-- strava_id: {id} -->` and a Strava link. HR-zone % is NOT
   in the API — omit it. If `splits_standard` was present, add a **Mile splits (pace · HR)**
   line (e.g. `1) 9:33 · 146 · 2) 8:37 · 153 · …`); otherwise omit it. For **Feel**, use
   `description` verbatim if present, else "(auto-import — no athlete note)". If
   `relative_effort`, `perceived_exertion`, `average_temp`, or `gear` are present, weave them
   in (effort/heat context, shoe).
   **If JR's note mentions pain or injury, raise the verdict to 🚩 and call it out.**

8. **Write the `index.html` Log tab** — insert a `data` row + `note` row at the top of
   `<tbody>` in `<table class="log-table">`, matching the existing pairs exactly:
   ```html
   <tr class="data">
     <td><strong>{Day Mon DD}</strong></td><td>{Type}</td><td>{prescribed short}</td><td><strong>{miles} mi</strong></td><td><strong>{pace}</strong></td><td>{avg}/{max} HR<br>{elev} ft</td><td class="v-ok|v-warn|v-flag">{✅|⚠️|🚩}</td>
   </tr>
   <tr class="note">
     <td colspan="7">{one-paragraph coach read}. <span class="feel">Feel: (auto-import — no athlete note)</span></td>
   </tr>
   ```
   Also refresh the `<div class="log-summary">` and the `<div class="log-week">` heading if
   the run starts a new week. Keep both logs telling the same story.

9. **Append the backup DB** — add one row to `data/log.csv` (header order:
   `date,day,week,type,prescribed,actual_mi,pace,moving_time,avg_hr,max_hr,elevation_ft,verdict,strava_id,relative_effort,feel,notes`).
   Use `date` as `YYYY-MM-DD`, `verdict` as `on-plan`/`off-plan`/`flag`; `relative_effort` =
   suffer_score if present else blank; `feel` = JR's `description` if present else blank.
   Quote any field that contains a comma. Append at the BOTTOM (oldest-first file).

10. **If a run warrants a plan change** (injury flag, repeated violations, clearly
    ahead/behind sub-4), edit the `index.html` Plan tab, then regenerate the plan backup:
    `python3 data/build_plan_csv.py`. Explain the change in the commit.

11. **Commit & push** (updates the live site + backup):
    ```bash
    git add training-log.md index.html data/log.csv data/plan.csv
    git commit -m "Log {Day} run from Strava: {one-line verdict}"
    git push
    ```

12. **Close the issue:**
    ```bash
    gh issue close {number} --comment "Logged → index.html + training-log.md + data/log.csv"
    ```

## Notes
- Keep verdicts in JR's voice: direct, specific paces, an **Action** line.
- If a body is malformed, comment on the issue what's missing and leave it open.

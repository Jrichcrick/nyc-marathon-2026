---
description: Ingest new Strava activities (filed as GitHub issues) into the training log
---

# /log-runs — Ingest Strava activities into the training log

Strava activities arrive as GitHub issues (Zapier files them, label `strava-activity`).
Process every open one into `training-log.md`, run the coach verdict against the plan,
commit, push, and close the issue. This is the automated coaching loop — act as JR's
coach per `CLAUDE.md`, not a generic logger.

## Steps

1. **Pull the queue:**
   ```bash
   gh issue list --label strava-activity --state open --json number,title,body --limit 50
   ```
   If empty, stop — nothing to do.

2. **For each issue**, parse the `key: value` body. Fields are RAW Strava units:
   - `strava_id` — dedupe key + builds the URL
   - `distance_m` (meters), `moving_time_s` / `elapsed_time_s` (seconds)
   - `total_elevation_gain_m` (meters), `average_speed_ms` / `max_speed_ms` (m/s)
   - `average_heartrate`, `max_heartrate`, `average_cadence`, `start_date_local`, `type`

3. **Convert:**
   - miles = `distance_m` / 1609.34
   - moving time = `moving_time_s` → `M:SS`
   - avg pace (min/mi) = (`moving_time_s` / 60) / miles → `M:SS/mi`
   - elevation (ft) = `total_elevation_gain_m` × 3.28084
   - Only `type: Run` activities go in the log. Rides/walks/other: close the issue with a
     comment "skipped — not a run", do not log.

4. **Dedupe:** if `training-log.md` already contains that `strava_id` (I stamp it in each
   entry as an HTML comment), skip and close the issue. Never double-log.

5. **Compare to the plan.** Open `marathon-training-nyc-2026.html`, find the prescribed
   workout for that date's day-of-week (see `CLAUDE.md` weekly schedule). Determine:
   - Was this the right day for this effort? (hard/easy principle is critical for JR)
   - Pace vs the prescribed zone for the current block (see paces in `CLAUDE.md`)
   - HR check: avg HR vs ~190 max. >~75% of effort in Z3+ on an easy day = intensity miss.
   - Distance vs prescribed.

6. **Write the entry** at the TOP of the current week's section in `training-log.md`,
   matching the existing format exactly. Use this skeleton (omit lines with no data —
   splits and HR-zone % are NOT in the API, so leave them out unless present):
   ```markdown
   ### {Day} {Mon DD} — {✅|⚠️|🚩} {one-line verdict}
   <!-- strava_id: {id} -->
   - **Prescribed:** {from plan}
   - **Actual:** {miles} mi @ {pace}/mi avg · {moving time} moving · {elev} ft gain
   - **HR (avg/max):** {avg} / {max}
   - **Feel:** (auto-import — no athlete note)
   - **Coach notes:** {real coaching read — right/wrong day, pace vs zone, HR signal, action}
   - [View on Strava](https://www.strava.com/activities/{id})
   ```
   Start a new `## Week N — <dates>` header if this run crosses into a new week.

7. **If the run reveals a needed plan change** (injury flag, repeated intensity violations,
   clearly ahead/behind sub-4 trajectory), adjust `marathon-training-nyc-2026.html` too and
   note why in the commit. Otherwise leave the plan as-is.

8. **Commit & push** (this updates the live site):
   ```bash
   git add training-log.md marathon-training-nyc-2026.html
   git commit -m "Log {Day} run from Strava: {one-line verdict}"
   git push
   ```

9. **Close the issue:**
   ```bash
   gh issue close {number} --comment "Logged → training-log.md"
   ```

## Notes
- One commit per run is fine; batch is fine too if several arrived at once.
- Keep verdicts in JR's voice/standard: direct, specific paces, an **Action** line.
- If a body is malformed/unparseable, comment on the issue what's missing and leave it open.

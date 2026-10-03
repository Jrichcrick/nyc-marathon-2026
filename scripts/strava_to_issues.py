#!/usr/bin/env python3
"""Poll Strava for recent activities and file each one as a GitHub issue.

Replaces the Zapier Zap that fed this repo. Emits the same issue title and
`key: value` body the /log-runs skill already parses, plus an `athlete:` key
so a roster of more than one athlete can share the pipeline.

Strava's API only ever returns the *authenticated* athlete's activities —
there is no endpoint that lists someone else's runs, and the API agreement
forbids using data for athletes who haven't authorized the app. So a second
athlete means a second refresh token, minted by that athlete themselves.

Required environment:
  STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN  (repo secrets)
  GITHUB_TOKEN, GITHUB_REPOSITORY                               (provided by Actions)
Optional:
  LOOKBACK_DAYS            how far back to scan (default 14)
  STRAVA_ATHLETE           slug for the primary athlete (default "jr")
  STRAVA_REFRESH_TOKEN_*   one per additional athlete; the suffix is the slug,
                           e.g. STRAVA_REFRESH_TOKEN_MATT -> athlete "matt".
                           Unset or empty is simply skipped, so a slot can sit
                           dormant in the workflow until the token exists.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

STRAVA = "https://www.strava.com"
API = "https://api.github.com"
LABEL = "strava-activity"
TOKEN_PREFIX = "STRAVA_REFRESH_TOKEN_"
DEFAULT_ATHLETE = "jr"


def http(url, *, data=None, headers=None, method=None):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read() or b"null")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:400]
            # Retry transient upstream failures; fail fast on everything else.
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise SystemExit(f"HTTP {e.code} from {url}\n{body}")
        except urllib.error.URLError:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise
    raise SystemExit(f"gave up on {url}")


REQUIRED = ("STRAVA_CLIENT_ID", "STRAVA_CLIENT_SECRET", "STRAVA_REFRESH_TOKEN")


def preflight():
    """Fail with a readable message rather than an opaque 400 from Strava."""
    missing = [k for k in REQUIRED if not os.environ.get(k, "").strip()]
    if missing:
        raise SystemExit(
            "Missing repository secret(s): " + ", ".join(missing) + "\n"
            "Add them under Settings -> Secrets and variables -> Actions.\n"
            "See README-strava-setup.md for how to obtain each value."
        )


def roster():
    """[(slug, refresh_token)] — the primary athlete first, then any extras.

    All athletes authorize the same Strava API application, so client id and
    secret are shared; only the refresh token differs.
    """
    primary = os.environ.get("STRAVA_ATHLETE", "").strip().lower() or DEFAULT_ATHLETE
    people = [(primary, os.environ["STRAVA_REFRESH_TOKEN"].strip())]
    for key, value in sorted(os.environ.items()):
        if not key.startswith(TOKEN_PREFIX) or not value.strip():
            continue
        slug = key[len(TOKEN_PREFIX):].lower()
        if slug and slug != primary:
            people.append((slug, value.strip()))
    return people


def strava_token(refresh_token):
    payload = urllib.parse.urlencode({
        "client_id": os.environ["STRAVA_CLIENT_ID"],
        "client_secret": os.environ["STRAVA_CLIENT_SECRET"],
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode()
    tok = http(f"{STRAVA}/oauth/token", data=payload, method="POST")
    return tok["access_token"]


def strava_get(path, token, **params):
    url = f"{STRAVA}/api/v3/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    return http(url, headers={"Authorization": f"Bearer {token}"})


def gh(path, token, *, data=None, method=None):
    body = json.dumps(data).encode() if data is not None else None
    return http(
        f"{API}{path}",
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "strava-ingest",
        },
    )


def already_filed(repo, token):
    """Every strava_id this repo has ever seen, open or closed."""
    seen, page = set(), 1
    while True:
        batch = gh(
            f"/repos/{repo}/issues?state=all&labels={LABEL}&per_page=100&page={page}",
            token,
        )
        if not batch:
            break
        for issue in batch:
            for line in (issue.get("body") or "").splitlines():
                if line.startswith("strava_id:"):
                    seen.add(line.split(":", 1)[1].strip())
                    break
        if len(batch) < 100:
            break
        page += 1
    return seen


def csv(values):
    """Strava arrays land as comma-joined lists, matching the Zapier format."""
    return ",".join("" if v is None else str(v) for v in values)


def build_body(a, slug):
    splits = a.get("splits_standard") or []
    laps = a.get("laps") or []
    fields = [
        ("athlete", slug),
        ("strava_id", a.get("id")),
        ("name", a.get("name")),
        ("type", a.get("type")),
        ("start_date_local", a.get("start_date_local")),
        ("distance_m", a.get("distance")),
        ("moving_time_s", a.get("moving_time")),
        ("elapsed_time_s", a.get("elapsed_time")),
        ("total_elevation_gain_m", a.get("total_elevation_gain")),
        ("average_speed_ms", a.get("average_speed")),
        ("max_speed_ms", a.get("max_speed")),
        ("average_heartrate", a.get("average_heartrate")),
        ("max_heartrate", a.get("max_heartrate")),
        ("average_cadence", a.get("average_cadence")),
        ("description", a.get("description")),
        ("perceived_exertion", a.get("perceived_exertion")),
        ("relative_effort", a.get("suffer_score")),
        ("average_temp", a.get("average_temp")),
        ("gear", (a.get("gear") or {}).get("name")),
    ]
    lines = [f"{k}: {'' if v is None else v}" for k, v in fields]
    if splits:
        lines += [
            "splits_distance_m: " + csv(s.get("distance") for s in splits),
            "splits_moving_time_s: " + csv(s.get("moving_time") for s in splits),
            "splits_avg_hr: " + csv(s.get("average_heartrate") for s in splits),
            "splits_elev_diff_m: " + csv(s.get("elevation_difference") for s in splits),
        ]
    if laps:
        lines += [
            "laps_distance_m: " + csv(l.get("distance") for l in laps),
            "laps_moving_time_s: " + csv(l.get("moving_time") for l in laps),
            "laps_avg_hr: " + csv(l.get("average_heartrate") for l in laps),
        ]
    return "\n".join(lines)


def file_activities(slug, refresh_token, repo, gh_token, lookback, seen, *, primary):
    """File one athlete's un-filed activities. Returns the number filed."""
    token = strava_token(refresh_token)
    after = int(time.time()) - lookback * 86400
    activities = strava_get("athlete/activities", token, after=after, per_page=100)
    print(f"[{slug}] Strava returned {len(activities)} activities in the last {lookback} days")

    filed = 0
    for summary in sorted(activities, key=lambda x: x.get("start_date", "")):
        sid = str(summary.get("id"))
        if sid in seen:
            continue
        # The summary payload has no splits, laps, or description — fetch the detail.
        a = strava_get(f"activities/{sid}", token)
        # JR's own titles stay exactly as Zapier wrote them; everyone else is
        # marked in the title so the issue list is readable at a glance.
        label = "Strava" if primary else f"Strava ({slug.title()})"
        title = f"{label}: {a.get('name')} — {a.get('start_date_local')}"
        gh(
            f"/repos/{repo}/issues",
            gh_token,
            data={"title": title, "body": build_body(a, slug), "labels": [LABEL]},
            method="POST",
        )
        print(f"  [{slug}] filed {sid}: {title}")
        seen.add(sid)
        filed += 1
    return filed


def main():
    repo = os.environ["GITHUB_REPOSITORY"]
    gh_token = os.environ["GITHUB_TOKEN"]
    lookback = int(os.environ.get("LOOKBACK_DAYS", "14"))

    preflight()
    people = roster()
    print("Roster: " + ", ".join(slug for slug, _ in people))

    seen = already_filed(repo, gh_token)
    print(f"{len(seen)} activities already filed in this repo")

    filed, failures = 0, []
    for index, (slug, refresh_token) in enumerate(people):
        # One athlete's revoked token must never stop the others from being
        # filed: this repo has already lost 8 days of runs to an ingest that
        # died quietly. Keep going, then exit non-zero so the Action goes red.
        try:
            filed += file_activities(
                slug, refresh_token, repo, gh_token, lookback, seen, primary=index == 0
            )
        except SystemExit as e:
            failures.append(f"{slug}: {e}")
        except Exception as e:
            failures.append(f"{slug}: {e.__class__.__name__}: {e}")

    print(f"Done. Filed {filed} new activit{'y' if filed == 1 else 'ies'}.")
    if failures:
        print(f"\nFailed for {len(failures)} athlete(s):")
        for failure in failures:
            print("  " + failure)
        print("Re-mint that athlete's refresh token; see README-strava-setup.md.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

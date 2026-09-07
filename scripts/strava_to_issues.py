#!/usr/bin/env python3
"""Poll Strava for recent activities and file each one as a GitHub issue.

Replaces the Zapier Zap that fed this repo. Emits exactly the same issue
title and `key: value` body the /log-runs skill already parses, so nothing
downstream has to change.

Required environment:
  STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN  (repo secrets)
  GITHUB_TOKEN, GITHUB_REPOSITORY                               (provided by Actions)
Optional:
  LOOKBACK_DAYS  how far back to scan (default 14)
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


def strava_token():
    payload = urllib.parse.urlencode({
        "client_id": os.environ["STRAVA_CLIENT_ID"],
        "client_secret": os.environ["STRAVA_CLIENT_SECRET"],
        "refresh_token": os.environ["STRAVA_REFRESH_TOKEN"],
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


def build_body(a):
    splits = a.get("splits_standard") or []
    laps = a.get("laps") or []
    fields = [
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


def main():
    repo = os.environ["GITHUB_REPOSITORY"]
    gh_token = os.environ["GITHUB_TOKEN"]
    lookback = int(os.environ.get("LOOKBACK_DAYS", "14"))

    preflight()
    token = strava_token()
    after = int(time.time()) - lookback * 86400
    activities = strava_get("athlete/activities", token, after=after, per_page=100)
    print(f"Strava returned {len(activities)} activities in the last {lookback} days")

    seen = already_filed(repo, gh_token)
    print(f"{len(seen)} activities already filed in this repo")

    filed = 0
    for summary in sorted(activities, key=lambda x: x.get("start_date", "")):
        sid = str(summary.get("id"))
        if sid in seen:
            continue
        # The summary payload has no splits, laps, or description — fetch the detail.
        a = strava_get(f"activities/{sid}", token)
        title = f"Strava: {a.get('name')} — {a.get('start_date_local')}"
        gh(
            f"/repos/{repo}/issues",
            gh_token,
            data={"title": title, "body": build_body(a), "labels": [LABEL]},
            method="POST",
        )
        print(f"  filed {sid}: {title}")
        filed += 1

    print(f"Done. Filed {filed} new activit{'y' if filed == 1 else 'ies'}.")


if __name__ == "__main__":
    sys.exit(main())

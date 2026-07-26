#!/usr/bin/env python3
"""Regenerate data/plan.csv from index.html (the source of truth).

index.html owns the plan; this script derives a flat, queryable backup table.
Re-run after any change to the Plan tab:  python3 data/build_plan_csv.py
"""
import csv
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = (ROOT / "index.html").read_text()

# Only parse the plan region (the Phase 1 header ... up to the course-notes marker).
plan_html = HTML[HTML.index("Phase 1 —"):HTML.index("<!-- COURSE NOTES -->")]

phase = ""
week = ""
week_dates = ""
week_target = ""
rows = []


def strip(s):
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).replace("&amp;", "&").strip()


def derive_type(w):
    lw = w.lower()
    if "race day" in lw:
        return "Race"
    if w.strip() == "Rest" or lw.startswith("rest"):
        return "Rest"
    if "boot camp" in lw or "squat" in lw:
        return "Cross-train"
    if "long run" in lw or lw.startswith("long"):
        return "Long"
    if "medium-long" in lw or "medium long" in lw:
        return "Medium-long"
    if "tempo" in lw:
        return "Tempo"
    if "×" in w or re.search(r"\bx\s*\d", lw) or "interval" in lw:
        return "Intervals"
    if "easy" in lw:
        return "Easy"
    return "Other"


def derive_miles(w):
    m = re.search(r"=\s*([\d.]+)\s*mi\b", w)        # "... = 7 mi total"
    if m:
        return m.group(1)
    m = re.search(r"\b([\d.]+)\s*mi\b", w)           # first "N mi" (not 100m)
    return m.group(1) if m else ""


# Walk the plan HTML line-anchored on the markers we care about.
for chunk in re.split(r"(<h2[^>]*>|<div class=\"wt\">|<div class=\"tag t-race\">|<tr[^>]*>)", plan_html):
    c = chunk.strip()
    mph = re.match(r"(Phase \d+ —[^<]*)</h2>", c)
    if mph:
        phase = mph.group(1).strip().replace("&amp;", "&")
    elif c.startswith("Race Week</h2>"):
        phase = "Race Week"
        week = "Race Week"
    h3 = re.search(r"<h3>Week\s*(\d+)\s*—\s*([^<]+)</h3>", c)
    if h3:
        week = f"Week {h3.group(1)}"
        week_dates = h3.group(2).strip()
    badge = re.search(r'class="badge[^"]*">~?([^<]+)</span>', c)
    if badge:
        week_target = badge.group(1).strip()
    if "October 26" in c and "November 1" in c:
        week, week_dates, week_target = "Race Week", "Oct 26 – Nov 1", "taper"
    day = re.search(r'<td class="dc">([^<]+)</td>\s*<td>(.*)', c, re.S)
    if day:
        date = day.group(1).strip()
        workout = strip(day.group(2))
        dow = date.split()[0]
        rows.append({
            "phase": phase, "week": week, "week_dates": week_dates,
            "week_target": week_target, "date": date, "day": dow,
            "workout": workout, "type": derive_type(workout),
            "distance_mi": derive_miles(workout),
        })

out = ROOT / "data" / "plan.csv"
with out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=[
        "phase", "week", "week_dates", "week_target",
        "date", "day", "workout", "type", "distance_mi"])
    w.writeheader()
    w.writerows(rows)

print(f"Wrote {len(rows)} day rows to {out}")

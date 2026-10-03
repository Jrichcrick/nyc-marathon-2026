# Strava → GitHub issues, without Zapier

The Zapier Zap that fed this repo went silent on Aug 30 2026 when Strava's
OAuth authorization expired on its own. `.github/workflows/strava-ingest.yml`
replaces it: a scheduled GitHub Action polls Strava directly and files each new
activity as an issue in exactly the format `/log-runs` already parses.

Nothing to disconnect, no monthly task limit, and when it breaks the logs are
in the Actions tab instead of somebody else's dashboard.

## One-time setup (~5 minutes)

### 1. Create a Strava API application

Go to <https://www.strava.com/settings/api>. If you've never made one, fill in
anything reasonable — the name doesn't matter, and "Authorization Callback
Domain" must be exactly `localhost`.

Note the **Client ID** and **Client Secret**.

### 2. Mint a refresh token

Strava's own tokens expire; a *refresh* token doesn't, and the workflow uses it
to mint a fresh access token on every run.

Open this URL in a browser, with your client ID substituted in:

```
https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read_all
```

Approve it. The browser will fail to load a `localhost` page — that's expected.
Copy the `code=` value out of the address bar.

Then exchange that code for tokens:

```bash
curl -X POST https://www.strava.com/oauth/token \
  -d client_id=YOUR_CLIENT_ID \
  -d client_secret=YOUR_CLIENT_SECRET \
  -d code=THE_CODE_FROM_THE_URL \
  -d grant_type=authorization_code
```

Copy the `refresh_token` from the response.

### 3. Add three repository secrets

Settings → Secrets and variables → Actions → **New repository secret**:

| Secret | Value |
|---|---|
| `STRAVA_CLIENT_ID` | from step 1 |
| `STRAVA_CLIENT_SECRET` | from step 1 |
| `STRAVA_REFRESH_TOKEN` | from step 2 |

### 4. Backfill the gap

Actions tab → **Strava ingest** → **Run workflow**. Set *lookback_days* to
cover the missing stretch (e.g. `30`) and run it. Everything Zapier missed gets
filed at once, then `/log-runs` picks it up as normal.

## Adding another athlete (e.g. a training partner)

**Strava will not hand you someone else's runs.** The API only returns the
authenticated athlete's activities; there is no endpoint that lists another
athlete's runs by ID, following them doesn't change that, and the API
agreement is explicit that you don't get data for athletes who haven't
authorized the app. The one shared-feed route, `/clubs/{id}/activities`,
returns no activity ID, no date, no HR and no splits, and names people only as
"First L." — useless for this log format.

So a second athlete is a second refresh token, and **they have to mint it
themselves.** It is a real ask: that token grants this repo read access to
their entire activity history, including private activities (`activity:read_all`).
Make sure they understand that before they hand it over, and that their runs
will be stored in this repo.

1. **They** do step 2 above — same authorize URL with *your* client ID, approved
   while signed into *their* Strava account — and send you the `refresh_token`.
   They never need your client secret: run the `curl` exchange yourself with the
   `code` they paste you, or send them the secret only if you'd rather they ran it.
2. Add it as `STRAVA_REFRESH_TOKEN_<NAME>`, e.g. **`STRAVA_REFRESH_TOKEN_MATT`**.
   The suffix, lowercased, becomes their tag: `athlete: matt`.
3. That's it for Matt — `.github/workflows/strava-ingest.yml` already passes that
   secret through, so the next scheduled run picks him up. For anyone else, add a
   matching line to the workflow's `env:` block first.

To stop ingesting someone, delete their secret — the slot going empty is skipped
silently. Ask them to revoke the app at <https://www.strava.com/settings/apps>
too; deleting the secret stops the reading, revoking ends the grant.

### What happens to their runs

Their activities are filed as issues with the same `strava-activity` label and an
`athlete:` key, then `/log-runs` routes on it: partner runs land in `data/log.csv`
with the `athlete` column set and nothing else. They never reach `training-log.md`
or the site's Training Log tab, and they are never given a coach verdict — the plan
and paces in `CLAUDE.md` are JR's. See "Whose run is it?" in
`.claude/commands/log-runs.md`.

If a partner's token expires, the ingest files everyone else's runs as normal and
*then* exits non-zero, so the Action goes red without one stale token silently
costing you your own runs — which is exactly how the Zap failure went unnoticed
for 8 days.

## How it behaves

- Runs every 3 hours; also runnable by hand from the Actions tab.
- Scans the last 14 days by default and files anything not already present.
- **Deduped by `strava_id`** against every issue in the repo, open or closed, so
  re-running is always safe and can never double-file a run.
- Issue title and body match the old Zapier output, including per-mile `splits_*`
  and watch `laps_*`, plus an `athlete:` key naming whose run it is. JR's own issue
  titles are unchanged; a partner's are prefixed, e.g. `Strava (Matt): …`.
- Multi-athlete: one refresh-token secret per athlete, each minted by that athlete.
  See "Adding another athlete" above.

## If it stops working

Check the Actions tab first — failures are visible there, unlike the Zap.
The usual cause is the refresh token being revoked (a Strava password change
deauthorizes every connected app). Redo step 2 and update the secret.

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

## How it behaves

- Runs every 3 hours; also runnable by hand from the Actions tab.
- Scans the last 14 days by default and files anything not already present.
- **Deduped by `strava_id`** against every issue in the repo, open or closed, so
  re-running is always safe and can never double-file a run.
- Issue title and body match the old Zapier output exactly, including per-mile
  `splits_*` and watch `laps_*`, so the `/log-runs` skill needs no changes.

## If it stops working

Check the Actions tab first — failures are visible there, unlike the Zap.
The usual cause is the refresh token being revoked (a Strava password change
deauthorizes every connected app). Redo step 2 and update the secret.

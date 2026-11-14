# Hosting the app for the judges (Vercel + Render + UptimeRobot)

**Read this if…** you are deploying the app, changing its public limits, or checking it is up.

Status: Approved 14 Nov 2026 (Yahya) · Owner: Yahya · Last reviewed 14 Nov 2026.

---

Public, no password ([backend design §10a](backend-design.md#10a-public-hosting-and-abuse-limits)). Everything below is on free plans; check each provider's current free-tier terms when signing up, because they change.

| Part | Where | Config in the repo |
|---|---|---|
| Frontend (static) | Vercel, project root `frontend/` | [`frontend/vercel.json`](../../frontend/vercel.json) |
| Backend API | Render free web service, Frankfurt | [`render.yaml`](../../render.yaml) |
| Keep the backend awake | UptimeRobot, 5-minute check | none |

The frontend calls the backend directly (`VITE_API_BASE` = the Render URL); the backend only accepts the Vercel origin (`MEG_CORS_ORIGINS`).

**Why it fits the free plan (measured 14 Nov):** one explore Promise Test uses about 0.04 s of CPU, a first Season Replay about 0.2 s, and the process peaks around 72 MB. Render's free plan sleeps after 15 minutes without traffic; the 5-minute ping keeps it awake, and one always-on service fits in the free monthly hours. The SQLite file is wiped on every redeploy or restart; that's fine for the demo (saved cards only need to last a visit).

## Steps

1. **Render (backend).** Dashboard → New → Blueprint → this GitHub repo. It reads `render.yaml`. When asked, set:
   - `MEG_CORS_ORIGINS`: leave as `http://localhost:5173` for now; you'll set the Vercel URL in step 4.
   - `MEG_GEMINI_API_KEY`: optional. Without it, voice uses the labelled keyword stand-in.

   Wait for the deploy, then open `https://<service>.onrender.com/api/v1/health`. It should show `"status":"ok"`.
2. **Gemini spending cap (if you set a key).** In Google Cloud, set a budget alert and an API quota on the key's project. The app's own ceiling (3,000 calls a day) is the first line; the provider cap is the backstop.
3. **Check the client address once.** Add the env var `MEG_DEBUG_CLIENT_IP=1` on Render and redeploy, then open `/api/v1/health` from your phone on mobile data. `client_ip` must be **your phone's public IP** (compare with any "what is my IP" site), not a `10.x`/`172.x`/Render address.
   - If it shows a Render-internal address, set `MEG_PROXY_HOPS=2` and check again.
   - Then **remove `MEG_DEBUG_CLIENT_IP`** and redeploy.

   Getting this wrong means every judge shares one limit, so don't skip it.
4. **Vercel (frontend).** Dashboard → Add New → Project → this repo.
   - Root Directory: `frontend` (it then reads `vercel.json`)
   - Environment variables: `VITE_API_BASE=https://<service>.onrender.com/api/v1` and `ENABLE_EXPERIMENTAL_COREPACK=1` (so Vercel uses the exact pnpm pinned in `package.json`)
   - Production branch: `main`

   Deploy, copy the URL (e.g. `https://mission-el-gheet.vercel.app`), then on Render set `MEG_CORS_ORIGINS` to exactly that URL (no trailing slash) and redeploy.
5. **UptimeRobot.** New monitor → type Keyword → URL `https://<service>.onrender.com/api/v1/health` → keyword `"status":"ok"` → every 5 minutes. Add your email for alerts. The health check is never rate-limited.
6. **Smoke test** on a phone: open the Vercel URL, run the UH-001 plan (berseem last cut 20 May 2027, maize 15 May 2027, keep the berseem). It must say **the plan has a conflict**. The "development build" badge must **not** appear; if it does, `VITE_API_BASE` wasn't set at build time.

## Limits (defaults; change with env vars, no code change)

| Group | Default | Env var |
|---|---|---|
| Voice (`/speech/interpret`) | 20 / minute and 300 / day per client; 3,000 / day in total | `MEG_LIMIT_SPEECH=20/300`, `MEG_SPEECH_DAILY_CEILING=3000` |
| Audio lookup (`/speech/tts`) | 60 / minute | `MEG_LIMIT_TTS=60` |
| Saving and checking (`POST /scenarios…`) | 30 / minute and 500 / day | `MEG_LIMIT_WRITE=30/500` |
| Everything else | 120 / minute | `MEG_LIMIT_READ=120` |
| Body size | 64 KB JSON, 256 KB voice clip (413 above) | none |
| All limits | on | `MEG_LIMITS=off` (local debugging only) |

A limit reply is 429 with `Retry-After`. Voice then switches to the pictures; every screen keeps working.

## Known limits of this setup

- Free Render instances can still restart occasionally; the first request after a restart takes up to about a minute.
- Restarts and redeploys reset the per-client counters (the daily voice ceiling resets only with a redeploy, since it lives in the SQLite file).
- Voice audio still goes to the browser's recogniser (Chrome sends it to Google); sending clips to Gemini (§8.2) is not built yet.

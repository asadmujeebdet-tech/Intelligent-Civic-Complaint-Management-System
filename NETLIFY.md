# Deploy CivicLens AI on Netlify

Netlify hosts the **frontend** (HTML/CSS/JS). The **API** (FastAPI + MongoDB + AI) must run on a separate host because Netlify does not support long-running Python servers or MongoDB.

**Recommended stack**

| Part | Platform | What it runs |
|------|----------|--------------|
| UI | **Netlify** | `frontend/` static site |
| API | **Render** (or Railway / Fly.io) | `run_api.py` + MongoDB Atlas |

Streamlit (`streamlit run app.py`) is for local/demo only — **not** deployable on Netlify.

---

## Step 1 — MongoDB Atlas (database)

1. Create a free cluster at [mongodb.com/atlas](https://www.mongodb.com/atlas).
2. Add a database user and allow network access (`0.0.0.0/0` for cloud APIs).
3. Copy the connection string, e.g.  
   `mongodb+srv://user:pass@cluster.mongodb.net/hackathon`

---

## Step 2 — Deploy the API (Render)

### Option A — One-click Blueprint

1. Push this repo to GitHub.
2. Go to [render.com](https://render.com) → **New** → **Blueprint**.
3. Connect the repo — Render reads `render.yaml`.
4. Set secret env vars when prompted:
   - `MONGO_URI` — Atlas connection string
   - `GEMINI_API_KEY` — Google Gemini key
   - `GOOGLE_MAP_API_KEY` — Google Maps (optional, for location autocomplete)
   - `EXTRA_ALLOWED_ORIGINS` — your Netlify URL, e.g. `https://civiclens.netlify.app`
5. Deploy and copy the service URL, e.g. `https://civiclens-api.onrender.com`.

### Option B — Manual Render Web Service

| Setting | Value |
|---------|--------|
| Build Command | `pip install -r requirements-api.txt` |
| Start Command | `python run_api.py` |
| Health Check | `/health` |

**Environment variables**

```
MONGO_URI=mongodb+srv://...
DB_NAME=hackathon
GEMINI_API_KEY=...
GOOGLE_MAP_API_KEY=...
EXTRA_ALLOWED_ORIGINS=https://your-site.netlify.app
```

Verify: open `https://YOUR-API.onrender.com/health` → `{"status":"healthy",...}`

> **Note:** Free Render services sleep after inactivity. First request after sleep can take 30–60s.

---

## Step 3 — Deploy the frontend (Netlify)

### From GitHub (recommended)

1. Go to [netlify.com](https://www.netlify.com) → **Add new site** → **Import an existing project**.
2. Connect your GitHub repo.
3. Netlify reads `netlify.toml` automatically (or set manually in the UI):

   | Setting | Value |
   |---------|--------|
   | Base directory | `/` |
   | Build command | `pip install -r requirements-build.txt && python build.py` |
   | Publish directory | `dist` |
   | Functions directory | `netlify/functions` |
4. Add **Environment variable** (required):

   | Key | Value |
   |-----|--------|
   | `API_URL` | `https://civiclens-api.onrender.com` (your Render URL, **no trailing slash**) |

5. Click **Deploy site**.

`build.py` copies `frontend/` → `dist/` and writes `dist/_redirects` so `/api/v1/...` on Netlify is proxied to your Render API.

> Use `requirements-build.txt` (not `requirements.txt`) on Netlify — the full `requirements.txt` installs ML packages and will slow or fail the build.

### From Netlify CLI

```bash
npm install -g netlify-cli
netlify login
netlify init
netlify env:set API_URL https://civiclens-api.onrender.com
netlify deploy --prod
```

---

## Step 4 — Verify

1. Open `https://your-site.netlify.app`
2. Home page loads with CivicLens styling and navbar
3. **Report Issue** — submit a test complaint
4. **Analytics** — dashboard KPIs and charts load
5. **Track Status** — search by complaint ID

If API calls fail:

- Netlify → **Deploys** → latest deploy → **Build log** — confirm `_redirects` was generated
- Confirm `API_URL` is set correctly (HTTPS, no trailing `/`)
- Confirm Render service is awake (`/health` returns 200)
- Check Render logs for MongoDB connection errors

---

## Environment variables summary

### Netlify

| Variable | Required | Example |
|----------|----------|---------|
| `API_URL` | Yes | `https://civiclens-api.onrender.com` |

### Render (API)

| Variable | Required | Example |
|----------|----------|---------|
| `MONGO_URI` | Yes | `mongodb+srv://...` |
| `DB_NAME` | Yes | `hackathon` |
| `GEMINI_API_KEY` | Yes | `AIza...` |
| `GOOGLE_MAP_API_KEY` | No | `AIza...` |
| `EXTRA_ALLOWED_ORIGINS` | Recommended | `https://your-site.netlify.app` |

---

## Custom domain (optional)

**Netlify:** Site settings → Domain management → Add custom domain  
**Render:** Service → Settings → Custom domain  

Update `EXTRA_ALLOWED_ORIGINS` on Render with the new Netlify domain and redeploy the API.

---

## Streamlit Cloud (optional shell)

If you also deploy on **Streamlit Cloud**, add this secret:

```toml
FRONTEND_URL = "https://your-site.netlify.app"
```

Streamlit will iframe your Netlify UI (same look as `run_server.py`).  
`API_URL` stays on **Netlify** only — not in Streamlit secrets.

See `.streamlit/secrets.toml.example`.

---

## Local development (unchanged)

```bash
python run_server.py          # UI + API at http://localhost:8000
streamlit run app.py          # Streamlit shell (embeds same UI)
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Build fails: `API_URL not set` | Add `API_URL` in Netlify env vars and redeploy |
| `Failed to load dashboard` | Wake Render API; check `/health` |
| Maps autocomplete empty | Set `GOOGLE_MAP_API_KEY` on Render |
| AI chatbot errors | Set `GEMINI_API_KEY` on Render |
| 502 on first request | Normal on Render free tier — wait and retry |

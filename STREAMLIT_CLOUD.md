# Streamlit Cloud + run_server UI

You get the **exact same Bootstrap UI** as `python run_server.py`, deployed through Streamlit Cloud.

Streamlit Cloud cannot run the FastAPI/HTML server by itself. The setup is:

```
┌─────────────────────┐      iframe       ┌──────────────────────────────┐
│  Streamlit Cloud    │  ──────────────►  │  Render (run_api.py)         │
│  app.py (shell)     │                   │  Same UI as run_server.py    │
│  yourapp.streamlit  │                   │  yourapp.onrender.com        │
└─────────────────────┘                   └──────────────────────────────┘
```

---

## Step 1 — MongoDB Atlas

1. Create a free cluster at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Allow network access `0.0.0.0/0`
3. Copy connection string → `MONGO_URI`

---

## Step 2 — Deploy full app on Render (~5 min)

1. Push this repo to GitHub
2. [render.com](https://render.com) → **New** → **Blueprint** → connect repo
3. Set secrets when asked:

| Variable | Example |
|----------|---------|
| `MONGO_URI` | `mongodb+srv://...` |
| `GEMINI_API_KEY` | your key |
| `GOOGLE_MAP_API_KEY` | optional |
| `EXTRA_ALLOWED_ORIGINS` | `https://yourapp.streamlit.app` |

4. Wait for deploy → copy URL, e.g. `https://civiclens-app.onrender.com`
5. Open that URL in browser — you should see the **same UI** as localhost:8000

> Free Render sleeps after 15 min idle. First load after sleep takes ~30–60s.

---

## Step 3 — Streamlit Cloud

1. [share.streamlit.io](https://share.streamlit.io) → **Create app**
2. Repo + branch + **Main file:** `app.py`
3. **Secrets:**

```toml
APP_URL = "https://civiclens-app.onrender.com"
```

4. Deploy

Your Streamlit URL now shows the full HTML UI inside an iframe — identical to `run_server.py`.

---

## Local development

```bash
# Option A — direct (best for dev)
python run_server.py
# → http://localhost:8000

# Option B — Streamlit shell (auto-starts local server)
streamlit run app.py
# → http://localhost:8501
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Blank iframe on Streamlit Cloud | Set `APP_URL` in secrets (Render URL, no trailing `/`) |
| "Cannot reach /health" | Wake Render app — open Render URL directly first |
| Port 8000 in use locally | Run only `streamlit run app.py` OR only `run_server.py`, not both |
| Iframe blocked | Set `EXTRA_ALLOWED_ORIGINS` on Render to your `*.streamlit.app` URL |

---

## Why two services?

| Platform | Role |
|----------|------|
| **Render** | Runs Python + FastAPI + MongoDB + serves `frontend/` (the awesome UI) |
| **Streamlit Cloud** | Thin wrapper required by your deploy target — embeds Render URL |

No Netlify needed. No native Streamlit forms — only the original HTML UI.

# Deploy CivicLens AI on Streamlit Cloud

This app runs **natively on Streamlit Cloud** — no Netlify, no iframe, no separate frontend host.

## Prerequisites

1. GitHub repo with this code
2. [MongoDB Atlas](https://www.mongodb.com/atlas) free cluster
3. Google **Gemini API** key (for AI features)

## Deploy steps

1. Push code to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **Create app**.
3. Select your repo, branch, and set **Main file path** to `app.py`.
4. Open **Advanced settings** → add secrets (copy from `.streamlit/secrets.toml.example`):

```toml
MONGO_URI = "mongodb+srv://..."
DB_NAME = "hackathon"
GEMINI_API_KEY = "..."
GOOGLE_MAP_API_KEY = "..."
```

5. Click **Deploy**.

First deploy may take several minutes (ML dependencies download).

## App structure

| File | Page |
|------|------|
| `app.py` | Home — hero, KPIs, quick actions |
| `pages/1_Report_Issue.py` | Submit complaint |
| `pages/2_Track_Status.py` | Track by ID + feedback |
| `pages/3_Analytics.py` | Dashboard with charts |
| `pages/4_Admin.py` | Manage complaints |

Navigation uses the **sidebar** (same pages as the HTML UI).

## Local development

```bash
# Streamlit (same as cloud)
streamlit run app.py

# Full HTML UI + API (optional)
python run_server.py
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Database connection failed | Check `MONGO_URI` in Secrets; allow `0.0.0.0/0` in Atlas Network Access |
| App crashes on startup | Check deploy logs; ensure `requirements.txt` installs cleanly |
| AI features fail | Set `GEMINI_API_KEY` in Secrets |
| Slow cold start | Normal on free tier — sentence-transformers loads on first run |

## Optional: HTML UI locally

`python run_server.py` still serves the original Bootstrap frontend at http://localhost:8000 for local use. Streamlit Cloud uses the native pages above.

"""Generate frontend/_redirects for Netlify API proxy (cross-platform)."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REDIRECTS = ROOT / "frontend" / "_redirects"

api_url = os.getenv("API_URL", "").strip().rstrip("/")
if not api_url:
    print("ERROR: Set API_URL in Netlify environment variables.")
    print("       Example: API_URL=https://civiclens-api.onrender.com")
    sys.exit(1)

REDIRECTS.write_text(f"/api/*  {api_url}/api/:splat  200!\n", encoding="utf-8")
print(f"Generated {REDIRECTS} -> {api_url}")

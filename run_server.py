"""
Netlify build script — copies frontend/ into dist/ and wires API proxy.

Netlify settings:
  Build command:  pip install -r requirements-build.txt && python build.py
  Publish dir:    dist
  Functions dir:  netlify/functions
"""
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "frontend"
DIST = ROOT / "dist"


def main() -> None:
    api_url = os.getenv("API_URL", "").strip().rstrip("/")

    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(
        FRONTEND,
        DIST,
        ignore=shutil.ignore_patterns("_redirects.example", "_redirects"),
    )

    redirects = DIST / "_redirects"
    if api_url:
        redirects.write_text(f"/api/*  {api_url}/api/:splat  200!\n", encoding="utf-8")
        print(f"[build] API proxy: /api/* -> {api_url}/api/*")
    else:
        print("[build] WARNING: API_URL not set — set it in Netlify env vars and redeploy.")
        redirects.write_text(
            "# API_URL missing — add in Netlify → Environment variables\n"
            "# Example: API_URL=https://civiclens-api.onrender.com\n",
            encoding="utf-8",
        )

    file_count = sum(1 for _ in DIST.rglob("*") if _.is_file())
    print(f"[build] Published {file_count} files to {DIST}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[build] ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

#!/usr/bin/env bash
# Generates Netlify _redirects to proxy /api/* to your hosted FastAPI backend.
set -euo pipefail

REDIRECTS_FILE="frontend/_redirects"

if [ -z "${API_URL:-}" ]; then
  echo "ERROR: Set API_URL in Netlify → Site settings → Environment variables"
  echo "       Example: API_URL=https://civiclens-api.onrender.com"
  exit 1
fi

API_URL="${API_URL%/}"
echo "/api/*  ${API_URL}/api/:splat  200!" > "$REDIRECTS_FILE"
echo "Generated ${REDIRECTS_FILE} → ${API_URL}"

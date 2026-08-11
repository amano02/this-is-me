#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

export VERCEL="${VERCEL:-1}"
export DJANGO_PRODUCTION="${DJANGO_PRODUCTION:-1}"

echo "==> Installing Python dependencies"
pip install -r requirements.txt

echo "==> Collecting static files"
python manage.py collectstatic --noinput

echo "==> Running migrations and seed"
python manage.py migrate --noinput
python manage.py seed_initial_data || true

echo "==> Build complete"

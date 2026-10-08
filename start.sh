#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/backend"
[ -f .env ] || cp .env.example .env
[ -d venv ] || python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACK=$!
trap "kill $BACK 2>/dev/null" EXIT
cd ../frontend
[ -d node_modules ] || npm install
echo "Browser me kholo: http://localhost:5173"
npm run dev

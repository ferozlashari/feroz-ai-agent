@echo off
setlocal
cd /d "%~dp0backend"
if not exist .env copy .env.example .env >nul
if not exist venv python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
start "Feroz Backend" cmd /k "uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

cd /d "%~dp0frontend"
if not exist node_modules call npm install
start "Feroz Frontend" cmd /k "npm run dev"

echo.
echo Browser me kholo: http://localhost:5173
echo (Pehli baar backend\.env me API keys daalna mat bhoolna)
pause

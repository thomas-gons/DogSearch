@echo off

:: Check for pip
where pip >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: "pip is not installed. Please install pip before continuing."
    exit /b 1
)

:: Check for Python 3.12
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: "Python is not installed. Please install Python 3.12 before continuing."
    exit /b 1
)

for /f "tokens=2 delims= " %%i in ('python --version 2^>^&1') do set python_version=%%i
if NOT "%python_version:~0,4%"=="3.12" (
    echo Error: "Python 3.12 is required. Found version: %python_version%"
    exit /b 1
)

:: Check for npm
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: "npm is not installed. Please install npm before continuing."
    exit /b 1
)

:: Create a virtual environment
cd backend
python -m venv .venv
call .venv\Scripts\activate.bat

:: Install dependencies
pip install -r requirements.txt
echo "To start the backend, you can run ``uvicorn main:app --host 0.0.0.0 --port 8000 --reload``"

:: Install frontend dependencies
cd ../frontend
npm install
echo "To start the frontend, you can run ``npm run dev``"

cd ..

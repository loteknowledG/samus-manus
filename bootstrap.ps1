<#
bootstrap.ps1 — setup Samus‑Manus dev environment (Windows PowerShell)
Run: powershell -ExecutionPolicy Bypass -File .\bootstrap.ps1

This script is idempotent and performs the following steps:
  1. checks Python >= 3.10
  2. creates a virtualenv at .venv (if missing)
  3. activates the venv for the script session
  4. upgrades pip and installs requirements
  5. runs quick verification and smoke checks
#>

$ErrorActionPreference = "Stop"

Write-Host "Samus‑Manus bootstrap — creating venv, installing requirements, running smoke checks..." -ForegroundColor Cyan

# Verify Python 3.10+
try {
    python -c "import sys; assert sys.version_info >= (3,10)
" | Out-Null
} catch {
    Write-Error "Python 3.10+ is required. Install Python 3.10+ and ensure 'python' is on PATH."
    exit 1
}

# Create virtual environment if missing
if (-not (Test-Path .venv)) {
    Write-Host "Creating virtual environment (.venv)..."
    python -m venv .venv
} else {
    Write-Host ".venv already exists — skipping venv creation."
}

# Activate venv for this script
Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

# Upgrade pip and install requirements
Write-Host "Upgrading pip and installing requirements..."
python -m pip install --upgrade pip
python -m pip install -r samus_manus_mvp/requirements.txt

# Quick verification of key optional modules
Write-Host "Verifying key libraries (pyttsx3, vosk, sounddevice)..."
python -c "import importlib
for m in ('pyttsx3','vosk','sounddevice'):
    ok = importlib.util.find_spec(m) is not None
    print(f'{m}: ' + ('OK' if ok else 'MISSING'))"

# Smoke checks: agent screenshot + TTS test
Write-Host "Running smoke checks: screenshot + voice test..."
python samus_manus_mvp/samus_agent.py --no-restore run "Take a screenshot" --no-approve
python samus_manus_mvp/voice_loop.py "Hello Samus — voice test"

Write-Host "\nBootstrap complete. If voice/STT failed, verify speakers, microphone, and that a Vosk model exists at samus_manus_mvp/model" -ForegroundColor Green

<#
bootup.ps1 - convenience script to run the project's boot sequence.

Usage examples:
  powershell -ExecutionPolicy Bypass -File .\bootup.ps1 -All           # install, screenshot, demo, voice
  powershell -ExecutionPolicy Bypass -File .\bootup.ps1 -Install -Screenshot
  powershell -ExecutionPolicy Bypass -File .\bootup.ps1 -Voice        # install voice deps then start voice_loop
  powershell -ExecutionPolicy Bypass -File .\bootup.ps1 -Yes -All     # non-interactive accept-all

Notes:
- Safety: pyautogui FAILSAFE is ON (move cursor to any screen corner to abort). Use Ctrl+C to interrupt.
- Default behavior (no switches) runs the sanity screenshot only.
#>

param(
    [switch]$Install,
    [switch]$Screenshot,
    [switch]$Demo,
    [switch]$Voice,
    [switch]$All,
    [switch]$Yes
)

function Confirm-Yes {
    param([string]$Message)
    if ($Yes) { return $true }
    $r = Read-Host "$Message [y/N]"
    return ($r -match '^[Yy]')
}

if ($All) { $Install = $true; $Screenshot = $true; $Demo = $true; $Voice = $true }
if (-not ($Install -or $Screenshot -or $Demo -or $Voice)) { $Screenshot = $true }

# ensure python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found in PATH. Install Python 3 and re-run this script."
    exit 1
}

# Install dependencies
if ($Install) {
    if (-not (Confirm-Yes "Install Python dependencies from requirements.txt (and voice requirements if -Voice)?")) {
        Write-Host "Skipping install step."
    } else {
        Write-Host "Upgrading pip..."
        & python -m pip install --upgrade pip
        if ($LASTEXITCODE -ne 0) { Write-Warning "pip upgrade failed (exit $LASTEXITCODE) - continuing." }

        Write-Host "Installing base requirements (requirements.txt)..."
        & python -m pip install -r .\requirements.txt
        if ($LASTEXITCODE -ne 0) { Write-Error "Failed to install base requirements (exit $LASTEXITCODE)."; exit $LASTEXITCODE }

        if ($Voice) {
            if (Test-Path .\requirements-voice.txt) {
                Write-Host "Installing voice requirements (requirements-voice.txt)..."
                & python -m pip install -r .\requirements-voice.txt
                if ($LASTEXITCODE -ne 0) { Write-Warning "Voice requirements install failed (exit $LASTEXITCODE)." }
            } else {
                Write-Warning "requirements-voice.txt not found; skipping voice requirements."
            }
        }
    }
}

# Sanity-check screenshot
if ($Screenshot) {
    Write-Host "Running sanity-check screenshot..."
    & python .\hands.py screenshot --out .\boot_check.png
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Saved: boot_check.png"
    } else {
        Write-Warning "Screenshot command failed (exit $LASTEXITCODE). See hands.py for details."
    }
}

# 60-second demo
if ($Demo) {
    if (Confirm-Yes "Run the 60-second demo (demo_60s.ps1)? This will move/click the mouse.") {
        Write-Host "Starting demo_60s.ps1..."
        & powershell -ExecutionPolicy Bypass -File .\demo_60s.ps1
    } else {
        Write-Host "Skipping demo."
    }
}

# Voice loop
if ($Voice) {
    if (Confirm-Yes "Start offline voice loop (voice_loop.py)? Press Enter to speak once running.") {
        Write-Host "Starting voice loop (Ctrl+C to stop)..."
        & python .\voice_loop.py
    } else {
        Write-Host "Skipping voice loop."
    }
}

Write-Host "Boot sequence finished."

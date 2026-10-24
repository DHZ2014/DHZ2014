# research-video skill installer for Windows (PowerShell 5+).
#
# One-line install (user-level: every Claude Code project on this PC can use it):
#   irm https://raw.githubusercontent.com/DHZ2014/DHZ2014/main/.claude/skills/research-video/install.ps1 | iex
#
# Options (set before running; they also work with the one-liner):
#   $env:RV_PROJECT_DIR = "D:\Finance Video"      # install only into that project's .claude\skills
#   $env:RV_BRANCH = "ccr-e9f92caf-juoyyl"         # install from another branch (default: main)
#   $env:RV_REPO_DIR = "D:\code\DHZ2014"           # where to keep the clone (default: %USERPROFILE%\DHZ2014)
#   $env:RV_NO_PROMPT = "1"                         # do not ask for the MiniMax key (for non-interactive runs)
#
# Re-run any time to update. Messages are in English on purpose: Windows PowerShell 5 reads
# scripts in the system code page, and Chinese text can turn into mojibake.
$Branch = if ($env:RV_BRANCH) { $env:RV_BRANCH } else { "main" }
$ProjectDir = $env:RV_PROJECT_DIR
$RepoDir = if ($env:RV_REPO_DIR) { $env:RV_REPO_DIR } else { "$env:USERPROFILE\DHZ2014" }
$ErrorActionPreference = "Stop"
$Repo = "https://github.com/DHZ2014/DHZ2014.git"

function Step($m) { Write-Host "`n==> $m" -ForegroundColor Yellow }
function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [Environment]::GetEnvironmentVariable("Path", "User") + ";" +
                "$env:LOCALAPPDATA\Microsoft\WinGet\Links"
}
function Have($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }
function Winget-Install($id) {
    if (-not (Have "winget")) { throw "winget not found. Install 'App Installer' from Microsoft Store, then re-run." }
    winget install -e --id $id --accept-source-agreements --accept-package-agreements --silent
    Refresh-Path
}

# 1. Git, Python, ffmpeg
Step "Checking Git / Python / ffmpeg"
Refresh-Path
if (-not (Have "git")) { Winget-Install "Git.Git" }
# Use the py launcher (plain "python" may be the Microsoft Store stub)
function Find-Py {
    $c = Get-Command py -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $c) { return $null }
    & $c.Source -3 --version *> $null
    if ($LASTEXITCODE -eq 0) { return $c.Source } else { return $null }
}
$PyExe = Find-Py
if (-not $PyExe) {
    Winget-Install "Python.Python.3.12"
    $PyExe = Find-Py
    if (-not $PyExe) { throw "Python installed but 'py' not on PATH yet. Close PowerShell, open a new one, re-run." }
}
if (-not (Have "ffmpeg")) { Winget-Install "Gyan.FFmpeg" }
if (-not (Have "ffmpeg")) { throw "ffmpeg installed but not on PATH yet. Close PowerShell, open a new one, re-run." }
function Invoke-Python { & $PyExe -3 @args; if ($LASTEXITCODE -ne 0) { throw "python $args failed" } }

# 2. Repository
Step "Getting DHZ2014/DHZ2014 ($Branch) into $RepoDir"
if (Test-Path "$RepoDir\.git") {
    git -C $RepoDir fetch origin $Branch
    git -C $RepoDir checkout $Branch
    git -C $RepoDir pull --ff-only origin $Branch
} else {
    git clone --branch $Branch $Repo $RepoDir
}
$Src = "$RepoDir\.claude\skills\research-video"
if (-not (Test-Path "$Src\SKILL.md")) { throw ("Skill not found in branch '$Branch'. Try: " + '$env:RV_BRANCH = "ccr-e9f92caf-juoyyl"') }

# 3. Install the skill (copy; re-run this script to update)
if ($ProjectDir) { $Dest = Join-Path $ProjectDir ".claude\skills\research-video" }
else { $Dest = "$env:USERPROFILE\.claude\skills\research-video" }
Step "Installing skill to $Dest"
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
robocopy $Src $Dest /E /XD fonts __pycache__ /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy failed ($LASTEXITCODE)" }
$global:LASTEXITCODE = 0

# 4. Python packages, browser, fonts
Step "Installing Python packages and fonts (a few minutes the first time)"
$env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"
Invoke-Python "$Dest\scripts\setup.py" --install

# 5. MiniMax key for the voiceover
if ($env:MINIMAX_API_KEY -and -not [Environment]::GetEnvironmentVariable("MINIMAX_API_KEY", "User")) {
    [Environment]::SetEnvironmentVariable("MINIMAX_API_KEY", $env:MINIMAX_API_KEY, "User")
}
if ($env:RV_NO_PROMPT) { Write-Host "Skipping the MiniMax key prompt (RV_NO_PROMPT). Set it later: setx MINIMAX_API_KEY <key>" }
elseif (-not [Environment]::GetEnvironmentVariable("MINIMAX_API_KEY", "User")) {
    Step "MiniMax API key (for the Chinese voiceover)"
    $k = Read-Host "Paste your MiniMax API key (Enter to skip)"
    if ($k) {
        [Environment]::SetEnvironmentVariable("MINIMAX_API_KEY", $k.Trim(), "User")
        Write-Host "Saved MINIMAX_API_KEY for your user account."
    }
}

Step "Done"
Write-Host "Skill: $Dest"
Write-Host "Restart the Claude desktop app, open your Finance Video project in Code mode, and say:"
Write-Host "  make a video from this research report  (attach the PDF)"

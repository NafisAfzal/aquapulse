@echo off
REM ============================================================
REM  AquaPulse GitHub Push Helper
REM  ============================================================
REM  This script helps you push your local AquaPulse repository
REM  to GitHub. Before running this script, you MUST:
REM  
REM  1. Create a new repository on GitHub.com (e.g., "aquapulse")
REM  2. Do NOT initialize it with a README, .gitignore, or license
REM  3. Copy the HTTPS or SSH clone URL from GitHub
REM  
REM  Then paste the URL when prompted below.
REM  ============================================================

echo.
echo AquaPulse GitHub Push Helper
echo =================================
echo.
echo Before proceeding:
echo   1. Create a repository on https://github.com (do NOT check "Initialize")
echo   2. Copy the clone URL (HTTPS or SSH)
echo.
set /p REPO_URL="Paste your GitHub repository URL here: "

echo.
echo Adding remote origin...
git remote add origin %REPO_URL%
echo.
echo Pushing to GitHub (this may take a moment)...
git push -u origin main

echo.
echo Push complete! Your repository is now live on GitHub.
echo Visit your repository URL in a browser to confirm.
echo.
pause

@echo off
cd /d "C:\Users\HARSH\Downloads\pixelsprout\pixelsprout"

set NTFY_TOPIC=pixelsprout-harsh-alerts-9f3k2

echo Pulling latest changes...
git pull
if errorlevel 1 (
    curl -d "git pull FAILED - check Pixelsprout automation manually" ntfy.sh/%NTFY_TOPIC%
    exit /b 1
)

echo Adding new games...
python auto-add-games.py
if errorlevel 1 (
    curl -d "auto-add-games.py FAILED - check Pixelsprout automation manually" ntfy.sh/%NTFY_TOPIC%
)

echo Posting to Pinterest...
python post-to-pinterest.py
if errorlevel 1 (
    curl -d "post-to-pinterest.py FAILED - check Pixelsprout automation manually" ntfy.sh/%NTFY_TOPIC%
)

echo Refreshing category pages...
python generate-category-pages.py
python add-category-pages-to-sitemap.py

echo Checking catalog quality...
python check-catalog-quality.py

echo Committing updates...
git add .
git commit -m "Daily automation update"
git push
if errorlevel 1 (
    curl -d "git push FAILED - possible conflict, check manually" ntfy.sh/%NTFY_TOPIC%
)

curl -d "Pixelsprout daily automation completed successfully" ntfy.sh/%NTFY_TOPIC%
echo Done.

@echo off
cd /d "C:\Users\HARSH\Downloads\pixelsprout\pixelsprout"

echo Pulling latest changes...
git pull

echo Adding new games...
python auto-add-games.py

echo Posting to Pinterest...
python post-to-pinterest.py

echo Refreshing category pages...
python generate-category-pages.py
python add-category-pages-to-sitemap.py

echo Committing category page updates...
git add .
git commit -m "Daily category page refresh"
git push

echo Done.

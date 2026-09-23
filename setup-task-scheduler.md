# Task Scheduler Setup — daily driver, replacing unreliable GitHub Actions

This runs both scripts from your own PC daily, using zero GitHub Actions minutes.
Only requirement: your PC needs to be on and awake at the scheduled time (or set
it to run on next login if the PC was off).

## Step 1: The batch file

`run-daily-automation.bat` is already in the repo. In order, it runs:

1. `git pull`
2. `python auto-add-games.py` — adds new games; also rebuilds the homepage and `/all-games/`
3. `python post-to-pinterest.py`
4. `python generate-category-pages.py` + `python add-category-pages-to-sitemap.py`
5. `python generate-homepage.py` — rebuilds `index.html` and `/all-games/` even on days with no new games
6. `python check-catalog-quality.py`
7. `git add` / `commit` / `push`, with ntfy.sh alerts on failure

The homepage is generated from `games-index.json` — never hand-edit `index.html`.

## Step 2: Open Task Scheduler

- Press `Win + R`, type `taskschd.msc`, hit Enter

## Step 3: Create the task

1. Click **"Create Task"** (not "Create Basic Task" — gives more control)
2. **General tab:**
   - Name: `Pixelsprout Daily Automation`
   - Check **"Run whether user is logged on or not"**
   - Check **"Run with highest privileges"**
3. **Triggers tab:** click New →
   - Begin the task: **On a schedule**
   - Daily, pick a time (e.g. 9:00 AM — whenever your PC is reliably on)
   - Check **"Enabled"**
4. **Actions tab:** click New →
   - Action: **Start a program**
   - Program/script: full path to the `.bat` file, e.g.
     `C:\Users\HARSH\Downloads\pixelsprout\pixelsprout\run-daily-automation.bat`
5. **Conditions tab:** uncheck "Start the task only if the computer is on AC power" (so it still runs on battery/laptop)
6. Click OK, enter your Windows password if prompted

## Step 4: Test it immediately

- Find the task in the list, right-click → **Run**
- Check the folder for updated files (`games-data.json`, `pinterest-posted.json`) to confirm it actually ran

## Notes
- If your PC is off at the scheduled time, it simply won't run that day — no error, just skipped. Consider checking in each morning if you're doing monk-mode study hours away from your PC.
- This fully replaces the need for GitHub Actions for daily automation. Keep the GitHub workflows in the repo as a backup — no harm in having both, since they share the same tracking files and won't double-post.

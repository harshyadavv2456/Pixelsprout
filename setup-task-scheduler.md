# Task Scheduler Setup — daily driver, replacing unreliable GitHub Actions

This runs both scripts from your own PC daily, using zero GitHub Actions minutes.
Only requirement: your PC needs to be on and awake at the scheduled time (or set
it to run on next login if the PC was off).

## Step 1: Create a batch file to run both scripts in sequence

Create a new file `run-daily-automation.bat` in your project folder:

```bat
@echo off
cd /d "C:\Users\HARSH\Downloads\pixelsprout\pixelsprout"
python auto-add-games.py
python post-to-pinterest.py
```

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

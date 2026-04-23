# Git & Heroku Setup Guide

## Prerequisites

### 1. Install Git
https://git-scm.com/download/win

During installation:
- ✅ Use Git Bash
- ✅ Add Git to PATH
- ✅ Use Windows-style line endings

### 2. Install Heroku CLI
https://devcenter.heroku.com/articles/heroku-cli

### 3. Create Heroku Account (Free)
https://signup.heroku.com/

---

## Step-by-Step Setup

### Step 1: Configure Git (First Time Only)

Open PowerShell and run:

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Example:
```powershell
git config --global user.name "Daksh"
git config --global user.email "daksh@example.com"
```

### Step 2: Navigate to Project

```powershell
cd C:\Users\daksh\OneDrive\Desktop\Projects\arbitrage-bot
```

### Step 3: Initialize Git Repository

```powershell
git init
```

Output:
```
Initialized empty Git repository in C:\Users\daksh\OneDrive\Desktop\Projects\arbitrage-bot\.git\
```

### Step 4: Add All Files

```powershell
git add .
```

This stages all files except those in `.gitignore`

### Step 5: Create Initial Commit

```powershell
git commit -m "Initial commit: Arbitrage bot ready for deployment"
```

Output:
```
[master (root-commit) abc1234] Initial commit: Arbitrage bot ready for deployment
 50 files changed, 5000+ insertions(+)
 ...
```

---

## Deploy to Heroku

### Step 1: Login to Heroku

```powershell
heroku login
```

This opens a browser window. Log in with your Heroku credentials.

### Step 2: Create Heroku App

```powershell
heroku create arbitrage-bot-yourname
```

**Replace `yourname` with your choice!**

Examples:
```powershell
heroku create arbitrage-bot-daksh
heroku create arbitrage-bot-crypto
heroku create arbitrage-bot-2024
```

Output:
```
Creating app... done, ⬢ arbitrage-bot-yourname
https://arbitrage-bot-yourname.herokuapp.com/ | https://git.heroku.com/arbitrage-bot-yourname.git
```

Save your app name! You'll need it later.

### Step 3: Deploy

```powershell
git push heroku main
```

If you get an error about `main` vs `master`:
```powershell
git branch -M main
git push heroku main
```

Wait for deployment to complete. You'll see:
```
remote: Building on the Heroku-20 stack
remote: Using buildpack: heroku/python
remote: -----> Installing requirements with pip
...
remote: -----> Verifying deploy... done.
To https://git.heroku.com/arbitrage-bot-yourname.git
```

### Step 4: Open Your App

```powershell
heroku open
```

Or visit: `https://arbitrage-bot-yourname.herokuapp.com`

---

## After Deployment

### View Logs

```powershell
heroku logs --tail
```

This shows real-time logs. Press `Ctrl+C` to stop.

### Check App Status

```powershell
heroku ps
```

Should show:
```
=== web (Free): gunicorn run:app (1)
web.1: up 2024/01/15 10:30:00 +0000 (~ 5s ago)
```

### Make Changes

```powershell
# Edit files locally

# Stage changes
git add .

# Commit
git commit -m "Description of changes"

# Deploy
git push heroku main
```

---

## Troubleshooting

### "Command not found: git"
- Git not installed or not in PATH
- Restart PowerShell after installing
- Try: `git --version`

### "Command not found: heroku"
- Heroku CLI not installed
- Restart PowerShell after installing
- Try: `heroku --version`

### Deployment hangs
- Wait a few minutes
- Check internet connection
- Try: `git push heroku main` again

### "Master branch not found"
```powershell
git branch -M main
git push heroku main
```

### App shows "Application Error"
```powershell
heroku logs --tail
```

Check the error message and refer to DEPLOYMENT.md

### Want to delete app?
```powershell
heroku apps:destroy --app arbitrage-bot-yourname
```

---

## Git Basics (If Needed)

### Check Status
```powershell
git status
```

### View Commit History
```powershell
git log --oneline
```

### Undo Last Commit (Before Push)
```powershell
git reset --soft HEAD~1
```

### View Changes
```powershell
git diff
```

---

## Useful Heroku Commands

```powershell
# List all apps
heroku apps

# View app info
heroku info --app arbitrage-bot-yourname

# Restart app
heroku restart --app arbitrage-bot-yourname

# View environment variables
heroku config --app arbitrage-bot-yourname

# Set environment variable
heroku config:set FLASK_ENV=production --app arbitrage-bot-yourname

# View metrics
heroku metrics --app arbitrage-bot-yourname
```

---

## Next Steps

1. ✅ Install Git and Heroku CLI
2. ✅ Create Heroku account
3. ✅ Initialize Git repository
4. ✅ Deploy to Heroku
5. ✅ Test your bot
6. ✅ Share the URL!

---

## Questions?

- Git: https://git-scm.com/doc
- Heroku: https://devcenter.heroku.com/
- See DEPLOYMENT.md for more help

---

**Happy deploying!** 🚀

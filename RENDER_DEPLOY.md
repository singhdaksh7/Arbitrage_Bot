# Deploy to Render

## Step 1: Push Code to GitHub

```powershell
cd C:\Users\daksh\OneDrive\Desktop\Projects\arbitrage-bot

# Initialize git
git init
git add .
git commit -m "Arbitrage Bot for Render"

# Add remote (replace YOUR_GITHUB_USERNAME)
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/arbitrage-bot.git

# Push
git branch -M main
git push -u origin main
```

## Step 2: Create Render Account & App

1. Go to https://render.com
2. Sign up with GitHub account
3. Click **New +**
4. Select **Web Service**
5. Connect your GitHub repo (arbitrage-bot)
6. Configure:
   - **Name:** arbitrage-bot
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`

## Step 3: Deploy

Click **Create Web Service** and wait 2-3 minutes.

Your bot will be live at: `https://arbitrage-bot-xxx.onrender.com`

## Done! 🚀

Your bot is now deployed to Render!

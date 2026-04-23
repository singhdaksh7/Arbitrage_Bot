# Arbitrage Bot - Heroku Deployment Guide

## ✅ Heroku Deployment Steps

### Prerequisites
1. **Heroku CLI** installed ([Download here](https://devcenter.heroku.com/articles/heroku-cli))
2. **Git** installed ([Download here](https://git-scm.com/))
3. Free **Heroku account** ([Sign up here](https://signup.heroku.com/))

---

## 📋 Step 1: Initialize Git Repository

Open PowerShell in your project folder and run:

```powershell
cd C:\Users\daksh\OneDrive\Desktop\Projects\arbitrage-bot

# Initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Arbitrage Bot"
```

---

## 🔐 Step 2: Login to Heroku

```powershell
heroku login
```

This will open a browser window to authenticate. Complete the login.

---

## 🚀 Step 3: Create Heroku App

```powershell
# Create a new Heroku app (replace 'arbitrage-bot-yourname' with your desired app name)
heroku create arbitrage-bot-yourname

# Verify the app was created
heroku apps
```

**Your app URL will be:** `https://arbitrage-bot-yourname.herokuapp.com`

---

## 📤 Step 4: Deploy to Heroku

```powershell
# Push your code to Heroku
git push heroku master

# (If using main branch instead of master:)
git push heroku main
```

**Wait for the deployment to complete.** You'll see output like:
```
remote: Building source...
remote: -----> Building on the Heroku-20 stack
remote: -----> Using buildpack: heroku/python
remote: ...
remote: Verifying deploy... done.
```

---

## ✅ Step 5: Open Your Deployed App

```powershell
# Open the app in your browser
heroku open

# Or visit directly:
# https://arbitrage-bot-yourname.herokuapp.com
```

---

## 📊 Step 6: Check Logs (If Something Goes Wrong)

```powershell
# View live logs
heroku logs --tail

# View recent logs
heroku logs
```

---

## 🔧 Configuration for Heroku

### Environment Variables (if needed later)

```powershell
# Set environment variables
heroku config:set FLASK_ENV=production

# View config
heroku config

# Unset a variable
heroku config:unset VARIABLE_NAME
```

### Database

The bot uses SQLite, which will be recreated on each dyno restart. For production persistence, consider upgrading to PostgreSQL:

```powershell
# Add PostgreSQL add-on (free tier available)
heroku addons:create heroku-postgresql:hobby-dev
```

---

## 📈 Scaling & Monitoring

```powershell
# Scale dynos (free tier = 1)
heroku ps:scale web=1

# View dyno status
heroku ps

# View metrics
heroku metrics
```

---

## 🆘 Troubleshooting

### App crashes after deployment?

```powershell
# Check the error logs
heroku logs --tail

# Restart the app
heroku restart

# Check dyno status
heroku ps
```

### "TemplateNotFound" error?

The templates should be found automatically. If not:
- Verify `Procfile` exists
- Check `runtime.txt` for Python version
- Redeploy: `git push heroku main`

### Want to update the code?

```powershell
# Make changes locally
# git add, commit changes

git push heroku main

# Check the deployment
heroku logs --tail
```

---

## 📝 Important Notes

### Free Tier Limitations

- **Dyno sleeps** after 30 minutes of inactivity
- **Rate limits** on API calls
- Limited database storage (20MB for SQLite)
- No SSL on custom domains (provided by Heroku)

### For Production

Consider upgrading to:
- **Hobby/Standard dynos** (not free)
- **PostgreSQL** for persistent data
- **Custom domain** with SSL

---

## 🎯 After Deployment

1. **Test the bot:** Visit `https://arbitrage-bot-yourname.herokuapp.com`
2. **Click "Scan Now"** to verify functionality
3. **Monitor logs:** `heroku logs --tail`
4. **Share the link:** Your bot is now publicly accessible!

---

## 📱 Access Your Deployed Bot

**Dashboard:** `https://arbitrage-bot-yourname.herokuapp.com`

**API Endpoints:**
- Status: `https://arbitrage-bot-yourname.herokuapp.com/api/status`
- Opportunities: `https://arbitrage-bot-yourname.herokuapp.com/api/opportunities`
- Scan: `https://arbitrage-bot-yourname.herokuapp.com/api/opportunities/scan`
- Wallet: `https://arbitrage-bot-yourname.herokuapp.com/api/wallet`

---

## 🔄 Continuous Deployment (Optional)

Connect GitHub for automatic deployments:

```powershell
# Create GitHub repo first, then:
heroku git:remote -a arbitrage-bot-yourname
git push heroku main
```

---

## 🛑 Stopping the App

```powershell
# Destroy the app (cannot be undone)
heroku apps:destroy --app arbitrage-bot-yourname

# Or just turn it off (keep the app)
heroku maintenance:on --app arbitrage-bot-yourname

# Turn maintenance off
heroku maintenance:off --app arbitrage-bot-yourname
```

---

## 🎓 Next Steps

1. **Monitor your deployment** with logs
2. **Test all endpoints** from your dashboard
3. **Share the link** with others
4. **Customize further** as needed
5. **Upgrade to paid tier** if you need more resources

---

**Congratulations! Your Arbitrage Bot is now deployed to Heroku! 🎉**

For more help: [Heroku Documentation](https://devcenter.heroku.com/)

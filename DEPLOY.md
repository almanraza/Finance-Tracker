# Backend Deployment Guide — Railway

## Step 1: Push to GitHub
```bash
cd finance-backend
git init
git add .
git commit -m "initial: FinanceAI FastAPI backend"
git remote add origin https://github.com/YOUR_USERNAME/financeai-backend.git
git push -u origin main
```

## Step 2: Deploy on Railway
1. Go to https://railway.app → New Project → Deploy from GitHub repo
2. Select your `financeai-backend` repo
3. Railway auto-detects the Dockerfile ✓

## Step 3: Add PostgreSQL
1. In your Railway project → + New → Database → PostgreSQL
2. Railway auto-sets `DATABASE_URL` in your service environment ✓

## Step 4: Set Environment Variables
In Railway → your service → Variables tab, add:

| Variable | Value |
|---|---|
| `SECRET_KEY` | (generate: `openssl rand -hex 32`) |
| `ANTHROPIC_API_KEY` | your Claude API key |
| `APP_ENV` | `production` |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` |

`DATABASE_URL` is set automatically by Railway when you add PostgreSQL.

## Step 5: Get your URL
After deploy → Settings → Domains → copy your URL
Example: `https://financeai-backend-production.up.railway.app`

## Step 6: Update Flutter app
Open `lib/config/env.dart`:
```dart
static const _env = Env.production;   // ← change this
static const _railwayUrl = 'https://financeai-backend-production.up.railway.app'; // ← paste your URL
```

## Step 7: Test the connection
Visit: `https://YOUR-URL.up.railway.app/health`
Should return: `{"status":"ok","version":"1.0.0","env":"production"}`

Visit: `https://YOUR-URL.up.railway.app/docs`
Full Swagger UI — test all endpoints here.

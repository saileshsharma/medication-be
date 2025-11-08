# Railway Environment Variables Setup

## Required Environment Variables

Set these in your Railway backend service:

### 1. Database Connection (Auto-provided by Railway)
Railway automatically provides these when you add PostgreSQL:
- `DATABASE_URL` - ✅ Auto-set by Railway

### 2. Redis Connection (Auto-provided by Railway)
Railway automatically provides these when you add Redis:
- `REDIS_URL` - ✅ Auto-set by Railway

### 3. Application Settings (Manual - Required)

Add these in Railway Dashboard → Your Backend Service → Variables:

```bash
SECRET_KEY=21c5230dd5d917cbe1b6dee48442619e840467d3bb615aca211823e1167ed9b5
DEBUG=False
ENVIRONMENT=production
```

### 4. API Keys (Optional)

If you have API keys for external services:

```bash
GOOGLE_FACT_CHECK_API_KEY=your_google_api_key_here
NEWS_API_KEY=your_news_api_key_here
```

## How to Set Variables in Railway

### Option 1: Railway Dashboard (Easiest)

1. Go to https://railway.app
2. Open your project
3. Click on your **backend service** (not Postgres or Redis)
4. Go to **Variables** tab
5. Click **+ New Variable**
6. Add each variable:
   - Name: `SECRET_KEY`
   - Value: `21c5230dd5d917cbe1b6dee48442619e840467d3bb615aca211823e1167ed9b5`
7. Click **Add**
8. Repeat for `DEBUG` and `ENVIRONMENT`
9. Railway will automatically redeploy

### Option 2: Railway CLI

```bash
# Make sure you're in the backend service
railway service

# Set variables
railway variables --set "SECRET_KEY=21c5230dd5d917cbe1b6dee48442619e840467d3bb615aca211823e1167ed9b5"
railway variables --set "DEBUG=False"
railway variables --set "ENVIRONMENT=production"
```

## Verify Configuration

After setting variables, check the deployment logs:

```bash
railway logs
```

You should see:
```
✅ Database initialized
🚀 Starting Pixel Pirates Backend v1.0.0
📚 API Documentation: http://0.0.0.0:8000/docs
```

## What Railway Provides Automatically

When you add services in Railway, these are auto-configured:

| Service | Variables Provided |
|---------|-------------------|
| PostgreSQL | `DATABASE_URL`, `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` |
| Redis | `REDIS_URL`, `REDIS_HOST`, `REDIS_PORT` |

Your backend is configured to use:
- `DATABASE_URL` for database connection ✅
- `REDIS_URL` for Redis connection ✅

No manual database configuration needed!

## Troubleshooting

### "Could not parse SQLAlchemy URL from string ''"

**Problem:** `DATABASE_URL` is not set

**Solution:** Railway should set this automatically. Check:
1. Postgres service is running
2. Backend service is in the same project
3. Railway may need to restart - go to Deployments → Restart

### "Redis connection failed"

**Problem:** `REDIS_URL` is not set

**Solution:** Railway should set this automatically. Check:
1. Redis service is running
2. Backend service is in the same project
3. Variables tab shows `REDIS_URL`

### Still having issues?

Check that all services are in the **same Railway project**:
```bash
railway status
```

Should show:
```
Project: PP (or your project name)
Service: [your backend service name]
```

## Next Steps

1. ✅ Set the 3 required manual variables (`SECRET_KEY`, `DEBUG`, `ENVIRONMENT`)
2. ✅ Wait for Railway to redeploy (automatic)
3. ✅ Generate a domain: `railway domain`
4. ✅ Test: `curl https://your-domain.railway.app/api/v1/health`

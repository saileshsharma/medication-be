# Railway Deployment - Complete Setup Guide

## ⚠️ IMPORTANT: Railway Does NOT Use .env Files

Railway injects environment variables directly at runtime. You MUST set them in the Railway Dashboard.

---

## 🎯 Exact Variables to Set in Railway Dashboard

### Step 1: Open Your Backend Service

1. Go to https://railway.app
2. Click on your project
3. Click on your **backend service** (NOT Postgres or Redis)
4. Click **"Variables"** tab

---

### Step 2: Add These EXACT Variables

Click **"+ New Variable"** for each one and copy-paste exactly:

#### Variable 1: Database Connection
```
Name: DATABASE_URL
Value: ${{Postgres.DATABASE_URL}}
```
**Note:** Use the EXACT service name. If your Postgres service is named "postgres" (lowercase), use `${{postgres.DATABASE_URL}}`

---

#### Variable 2: Redis Connection
```
Name: REDIS_URL
Value: ${{Redis.REDIS_URL}}
```
**Note:** Use the EXACT service name. If your Redis service is named "redis" (lowercase), use `${{redis.REDIS_URL}}`

---

#### Variable 3: Secret Key
```
Name: SECRET_KEY
Value: 21c5230dd5d917cbe1b6dee48442619e840467d3bb615aca211823e1167ed9b5
```

---

#### Variable 4: Debug Mode
```
Name: DEBUG
Value: False
```

---

#### Variable 5: Environment
```
Name: ENVIRONMENT
Value: production
```

---

## 🔍 How to Find Your Service Names

If `${{Postgres.DATABASE_URL}}` doesn't work, your services might have different names.

### Check Service Names:

1. In Railway Dashboard, look at the service cards in your project
2. Common variations:
   - **Postgres:** `Postgres`, `postgres`, `PostgreSQL`, `database`
   - **Redis:** `Redis`, `redis`, `cache`

### Find Variables in Other Services:

1. Click on your **Postgres** service
2. Go to **Variables** tab
3. Look for `DATABASE_URL` - copy the exact service name from the reference

**Example:** If you see `${{postgres.DATABASE_URL}}` in the Postgres service, use that exact format.

---

## ✅ Verification Checklist

After adding all 5 variables:

- [ ] `DATABASE_URL` is set with service reference `${{...}}`
- [ ] `REDIS_URL` is set with service reference `${{...}}`
- [ ] `SECRET_KEY` is set (64-character hex string)
- [ ] `DEBUG` is set to `False`
- [ ] `ENVIRONMENT` is set to `production`

---

## 🚀 After Setting Variables

Railway will automatically trigger a new deployment.

### Watch the Deployment:

```bash
railway logs --follow
```

### Expected Output (Success):

```
🚀 Starting Pixel Pirates Backend v1.0.0
📝 Environment: production
🔧 Debug mode: False
✅ Database initialized
📚 API Documentation: http://0.0.0.0:8000/docs
```

### If You See Errors:

#### Error: "Could not parse SQLAlchemy URL from string ''"
**Problem:** `DATABASE_URL` is empty

**Solution:**
1. Check that `DATABASE_URL = ${{Postgres.DATABASE_URL}}` is set
2. Verify Postgres service is running
3. Try exact service name: `${{postgres.DATABASE_URL}}`

---

#### Error: "Redis connection failed"
**Problem:** `REDIS_URL` is not set or wrong

**Solution:**
1. Check that `REDIS_URL = ${{Redis.REDIS_URL}}` is set
2. Verify Redis service is running
3. Try exact service name: `${{redis.REDIS_URL}}`

---

#### Error: "error parsing value for field 'CORS_ORIGINS'"
**Problem:** This error is already fixed in the latest code

**Solution:** Make sure your code is up to date (we just pushed the fix)

---

## 📸 Visual Guide

### Where to Set Variables:

```
Railway Dashboard
└── Your Project
    └── Backend Service (click this)
        └── Variables tab (click this)
            └── + New Variable (click this)
                ├── Name: DATABASE_URL
                └── Value: ${{Postgres.DATABASE_URL}}
```

---

## 🔄 Alternative: Use Railway CLI

If you prefer CLI:

```bash
# Make sure you're in backend service
railway service

# Set variables one by one
railway variables --set "DATABASE_URL=\${{Postgres.DATABASE_URL}}"
railway variables --set "REDIS_URL=\${{Redis.REDIS_URL}}"
railway variables --set "SECRET_KEY=21c5230dd5d917cbe1b6dee48442619e840467d3bb615aca211823e1167ed9b5"
railway variables --set "DEBUG=False"
railway variables --set "ENVIRONMENT=production"
```

**Note:** Escape the `$` with backslash: `\${{...}}`

---

## 📋 Current Status Check

Run this to see your current variables:

```bash
railway variables
```

You should see all 5 variables listed.

---

## 🆘 Still Having Issues?

### Take a Screenshot

1. Go to Railway Dashboard → Your Backend Service → Variables tab
2. Take a screenshot showing all variables
3. Share the screenshot (with SECRET_KEY blurred)

### Share Logs

```bash
railway logs
```

Copy the last 50 lines and share them.

---

## 🎯 Quick Copy-Paste for Railway Dashboard

**All 5 Variables:**

| Name | Value |
|------|-------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` |
| `SECRET_KEY` | `21c5230dd5d917cbe1b6dee48442619e840467d3bb615aca211823e1167ed9b5` |
| `DEBUG` | `False` |
| `ENVIRONMENT` | `production` |

---

**After setting these, Railway will deploy successfully!** 🚀

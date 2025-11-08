# 🚀 Quick Deployment Guide

Choose your platform and get deployed in minutes!

## 🎯 Recommended Choice

### For Quick Start: **Railway** ⭐
**Cost:** Free $5 credit monthly
**Time:** 5 minutes
**Difficulty:** Easy

```bash
./deploy.sh
# Select option 1
```

That's it! Railway handles everything.

---

## 📋 All Options at a Glance

### 1️⃣ Railway (Easiest)
```bash
npm i -g @railway/cli
railway login
railway init
railway add --database postgresql
railway add --database redis
railway variables set SECRET_KEY=$(openssl rand -hex 32)
railway up
```
**Cost:** $5-15/month
**URL:** https://your-app.railway.app

---

### 2️⃣ Render (Best Free Tier)
```bash
git push origin main
# Go to render.com → New Blueprint → Select repo
# Set SECRET_KEY in dashboard
```
**Cost:** Free tier available
**URL:** https://your-app.onrender.com

---

### 3️⃣ Fly.io (Global Edge)
```bash
fly auth login
fly launch --no-deploy
fly postgres create --name pixelpirates-db
fly postgres attach pixelpirates-db
fly redis create
fly secrets set SECRET_KEY=$(openssl rand -hex 32)
fly deploy
```
**Cost:** Free tier (3 VMs)
**URL:** https://your-app.fly.dev

---

### 4️⃣ DigitalOcean (Professional)
```bash
doctl auth init
doctl apps create --spec .do/app.yaml
# Set secrets in dashboard
```
**Cost:** $12-20/month
**URL:** Custom or *.ondigitalocean.app

---

### 5️⃣ AWS (Enterprise)
```bash
# Build and push to ECR
aws ecr create-repository --repository-name pixelpirates-backend
docker build -f Dockerfile.prod -t pixelpirates-backend .
docker tag pixelpirates-backend:latest ACCOUNT.dkr.ecr.REGION.amazonaws.com/pixelpirates-backend
docker push ACCOUNT.dkr.ecr.REGION.amazonaws.com/pixelpirates-backend

# Deploy to App Runner
aws apprunner create-service --cli-input-json file://aws-apprunner.json
```
**Cost:** $20+/month
**URL:** Custom domain recommended

---

## 🔧 One-Command Deployment

Use our automated script:

```bash
cd pixel-pirates-backend
./deploy.sh
```

Select your platform (1-5) and follow the prompts!

---

## 🔑 Required Environment Variables

All platforms need these:

```bash
# Required
SECRET_KEY=<generate with: openssl rand -hex 32>
DATABASE_URL=<auto-provided by most platforms>
REDIS_HOST=<auto-provided by most platforms>
DEBUG=False
ENVIRONMENT=production

# Optional
GOOGLE_FACT_CHECK_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
```

---

## 📱 Update Mobile App After Deployment

Edit `pixel-pirates-app/src/services/api.ts`:

```typescript
const API_BASE_URL = __DEV__
  ? Platform.select({
      ios: 'http://localhost:8000/api/v1',
      android: 'http://10.0.2.2:8000/api/v1',
    })
  : 'https://YOUR-PRODUCTION-URL.com/api/v1';  // ← Update this!
```

Replace `YOUR-PRODUCTION-URL.com` with your actual deployment URL.

---

## ✅ Test Your Deployment

```bash
# Health check
curl https://your-api-url.com/api/v1/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "healthy",
  "redis": "healthy"
}
```

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Tier | Best For |
|----------|-----------|-----------|----------|
| Railway | $5 credit | $5-15/mo | Quick start |
| Render | 750 hrs/mo | $7+/mo | Budget-friendly |
| Fly.io | 3 VMs | $5-10/mo | Global apps |
| DigitalOcean | $200 credit (60d) | $12-20/mo | Professional |
| AWS | 12 months free | $20+/mo | Enterprise |
| Google Cloud | $300 credit | Pay-per-use | Serverless |

---

## 🆘 Common Issues

### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000
# Kill it or change port in docker-compose.prod.yml
```

### Database Connection Failed
```bash
# Check if DATABASE_URL is set correctly
railway variables  # or platform-specific command

# Test connection
psql $DATABASE_URL
```

### Build Failed
```bash
# Clear cache and rebuild
docker-compose down -v
docker-compose build --no-cache
```

### Health Check Timeout
```bash
# Increase start_period in docker-compose files
healthcheck:
  start_period: 60s  # Was 40s
```

---

## 📊 Monitoring Your App

**Railway:**
```bash
railway logs
railway status
```

**Render:**
- Go to dashboard → Logs tab

**Fly.io:**
```bash
fly logs
fly status
```

**DigitalOcean:**
```bash
doctl apps logs YOUR_APP_ID --follow
```

---

## 🔒 Security Checklist

Before going live:

- [ ] Strong `SECRET_KEY` generated (32+ chars)
- [ ] Strong database password
- [ ] HTTPS enabled (automatic on most platforms)
- [ ] CORS restricted to your domain
- [ ] Database backups enabled
- [ ] Rate limiting verified (already in backend)
- [ ] API keys stored as secrets
- [ ] No secrets in git repository
- [ ] Health monitoring set up
- [ ] Error tracking configured

---

## 🎯 Recommended Path

1. **Start Here:** Railway (easiest, free tier)
2. **Scale Up:** Fly.io or Render (global edge, better free tier)
3. **Production:** DigitalOcean (reliable, professional)
4. **Enterprise:** AWS or Google Cloud (full control, advanced features)

---

## 📚 Need More Help?

- **Full Guide:** See `DEPLOYMENT.md` for detailed instructions
- **Docker Guide:** See `DOCKER_USAGE.md` for local deployment
- **API Docs:** https://your-api.com/docs (FastAPI auto-generates)
- **Backend README:** See `README.md` for features and setup

---

## 🎉 You're Ready!

Your backend is production-ready and optimized. Pick a platform and deploy! 🚀

**Fastest route:**
```bash
./deploy.sh
```
Select option 1 (Railway) and you'll be live in 5 minutes!

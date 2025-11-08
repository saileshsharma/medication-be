# Production Deployment Guide

Complete guide for deploying Pixel Pirates Backend to production.

## 🎯 Quick Comparison

| Platform | Best For | Free Tier | Cost/Month | Setup Time | Difficulty |
|----------|----------|-----------|------------|------------|------------|
| **Railway** | Quick start | $5 credit | $5-15 | 5 min | ⭐ Easy |
| **Render** | Budget-friendly | 750 hrs | Free-$7 | 10 min | ⭐ Easy |
| **Fly.io** | Global edge | 3 VMs | Free-$10 | 15 min | ⭐⭐ Medium |
| **DigitalOcean** | Balanced | $200 credit | $12-20 | 20 min | ⭐⭐ Medium |
| **AWS** | Enterprise | 12 months | $20+ | 60 min | ⭐⭐⭐ Hard |
| **Google Cloud** | Serverless | $300 credit | Pay-per-use | 30 min | ⭐⭐ Medium |

## 🚀 Option 1: Railway (Recommended for Beginners)

### Prerequisites
- GitHub account
- Railway account (free)

### Step-by-Step

1. **Push to GitHub**
   ```bash
   cd pixel-pirates-backend
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/pixel-pirates-backend.git
   git push -u origin main
   ```

2. **Install Railway CLI**
   ```bash
   npm i -g @railway/cli
   railway login
   ```

3. **Initialize Project**
   ```bash
   railway init
   railway link
   ```

4. **Add Database Services**
   ```bash
   # Add PostgreSQL
   railway add --database postgres

   # Add Redis
   railway add --database redis
   ```

5. **Set Environment Variables**
   ```bash
   # Generate secret key
   railway variables set SECRET_KEY=$(openssl rand -hex 32)

   # Optional API keys
   railway variables set GOOGLE_FACT_CHECK_API_KEY=your_key_here
   railway variables set NEWS_API_KEY=your_key_here

   # Production settings
   railway variables set DEBUG=False
   railway variables set ENVIRONMENT=production
   ```

6. **Deploy**
   ```bash
   railway up
   ```

7. **Get Your URL**
   ```bash
   railway open
   # Or get domain programmatically
   railway domain
   ```

### Test Deployment
```bash
curl https://your-app.railway.app/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "healthy",
  "redis": "healthy"
}
```

---

## 🎨 Option 2: Render

### Step-by-Step

1. **Create render.yaml** (already created in repo)

2. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push -u origin main
   ```

3. **Deploy via Dashboard**
   - Go to https://render.com
   - Click "New +" → "Blueprint"
   - Connect your GitHub repo
   - Render will detect `render.yaml` and create all services

4. **Set Secrets**
   - Go to Backend service → Environment
   - Add:
     - `SECRET_KEY` (generate with `openssl rand -hex 32`)
     - `GOOGLE_FACT_CHECK_API_KEY` (optional)
     - `NEWS_API_KEY` (optional)

5. **Deploy**
   - Automatic on git push
   - Or manual: Dashboard → Deploy Latest Commit

### Custom Domain (Optional)
- Settings → Custom Domain → Add your domain
- Update DNS: CNAME to `your-app.onrender.com`

---

## 🌍 Option 3: Fly.io

### Prerequisites
- Fly.io account
- Credit card (required even for free tier)

### Step-by-Step

1. **Install Fly CLI**
   ```bash
   # macOS
   brew install flyctl

   # Linux/WSL
   curl -L https://fly.io/install.sh | sh

   # Windows
   pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **Login and Launch**
   ```bash
   fly auth login
   cd pixel-pirates-backend
   fly launch --no-deploy
   ```

3. **Create PostgreSQL**
   ```bash
   fly postgres create --name pixelpirates-db --region sjc
   fly postgres attach pixelpirates-db
   ```

4. **Create Redis (via Upstash)**
   ```bash
   fly redis create
   # Follow prompts to select plan (free tier available)
   ```

5. **Set Secrets**
   ```bash
   fly secrets set SECRET_KEY=$(openssl rand -hex 32)
   fly secrets set GOOGLE_FACT_CHECK_API_KEY=your_key_here
   fly secrets set NEWS_API_KEY=your_key_here
   ```

6. **Deploy**
   ```bash
   fly deploy
   ```

7. **Check Status**
   ```bash
   fly status
   fly logs
   fly open /api/v1/health
   ```

### Scale Up/Down
```bash
# Scale to 2 instances
fly scale count 2

# Scale memory
fly scale memory 512

# Auto-scale
fly autoscale set min=1 max=3
```

---

## 🌊 Option 4: DigitalOcean App Platform

### Step-by-Step

1. **Install doctl CLI**
   ```bash
   # macOS
   brew install doctl

   # Linux
   cd ~
   wget https://github.com/digitalocean/doctl/releases/download/v1.98.0/doctl-1.98.0-linux-amd64.tar.gz
   tar xf ~/doctl-1.98.0-linux-amd64.tar.gz
   sudo mv ~/doctl /usr/local/bin
   ```

2. **Authenticate**
   ```bash
   doctl auth init
   # Enter your API token from DigitalOcean dashboard
   ```

3. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push -u origin main
   ```

4. **Update .do/app.yaml**
   - Replace `your-username/pixel-pirates-backend` with your GitHub repo

5. **Create Databases**
   ```bash
   # PostgreSQL
   doctl databases create pixelpirates-db \
     --engine pg \
     --region nyc3 \
     --size db-s-1vcpu-1gb

   # Redis
   doctl databases create pixelpirates-redis \
     --engine redis \
     --region nyc3 \
     --size db-s-1vcpu-1gb
   ```

6. **Deploy App**
   ```bash
   doctl apps create --spec .do/app.yaml
   ```

7. **Set Secrets**
   - Go to DigitalOcean Dashboard
   - Apps → Your App → Settings → Environment Variables
   - Add encrypted variables:
     - `SECRET_KEY`
     - `DATABASE_URL` (from database connection string)
     - `REDIS_HOST` (from Redis database)

8. **Monitor**
   ```bash
   doctl apps list
   doctl apps logs YOUR_APP_ID
   ```

---

## ☁️ Option 5: AWS (Advanced)

### Prerequisites
- AWS Account
- AWS CLI installed
- Docker installed

### Option A: AWS App Runner (Easier)

1. **Install AWS CLI**
   ```bash
   # macOS
   brew install awscli

   # Linux
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```

2. **Configure AWS**
   ```bash
   aws configure
   # Enter: Access Key, Secret Key, Region (us-east-1), Format (json)
   ```

3. **Create ECR Repository**
   ```bash
   aws ecr create-repository --repository-name pixelpirates-backend
   ```

4. **Build and Push Docker Image**
   ```bash
   # Get login
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

   # Build
   docker build -f Dockerfile.prod -t pixelpirates-backend .

   # Tag
   docker tag pixelpirates-backend:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/pixelpirates-backend:latest

   # Push
   docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/pixelpirates-backend:latest
   ```

5. **Create RDS PostgreSQL**
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier pixelpirates-db \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username postgres \
     --master-user-password YOUR_PASSWORD \
     --allocated-storage 20
   ```

6. **Create ElastiCache Redis**
   ```bash
   aws elasticache create-cache-cluster \
     --cache-cluster-id pixelpirates-redis \
     --cache-node-type cache.t3.micro \
     --engine redis \
     --num-cache-nodes 1
   ```

7. **Deploy to App Runner**
   ```bash
   # Update aws-apprunner.json with your image URI
   aws apprunner create-service --cli-input-json file://aws-apprunner.json
   ```

### Option B: AWS ECS Fargate (Production)

1. **Create ECS Cluster**
   ```bash
   aws ecs create-cluster --cluster-name pixelpirates-cluster
   ```

2. **Register Task Definition**
   ```bash
   # Update aws-ecs-task-definition.json with your account ID
   aws ecs register-task-definition --cli-input-json file://aws-ecs-task-definition.json
   ```

3. **Create Application Load Balancer**
   ```bash
   aws elbv2 create-load-balancer \
     --name pixelpirates-alb \
     --subnets subnet-xxxx subnet-yyyy \
     --security-groups sg-xxxx
   ```

4. **Create ECS Service**
   ```bash
   aws ecs create-service \
     --cluster pixelpirates-cluster \
     --service-name pixelpirates-api \
     --task-definition pixelpirates-backend \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxx],securityGroups=[sg-xxxx],assignPublicIp=ENABLED}"
   ```

---

## 🔧 Post-Deployment Configuration

### Update Mobile App API URL

Edit `pixel-pirates-app/src/services/api.ts`:

```typescript
const API_BASE_URL = __DEV__
  ? Platform.select({
      ios: 'http://localhost:8000/api/v1',
      android: 'http://10.0.2.2:8000/api/v1',
    })
  : 'https://your-production-api.com/api/v1';  // ← Update this!
```

### Add Environment Variables

All platforms need these variables:

**Required:**
- `SECRET_KEY` - Generate with `openssl rand -hex 32`
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_HOST` - Redis hostname
- `DEBUG` - Set to `False`
- `ENVIRONMENT` - Set to `production`

**Optional:**
- `GOOGLE_FACT_CHECK_API_KEY` - For fact-checking features
- `NEWS_API_KEY` - For news verification

### Enable CORS for Mobile App

Backend already has CORS configured in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, update to:
```python
allow_origins=[
    "https://your-domain.com",
    "capacitor://localhost",  # For mobile apps
    "ionic://localhost",
]
```

---

## 🔒 Security Checklist

- [ ] Generate strong `SECRET_KEY` (32+ characters)
- [ ] Use strong database password
- [ ] Enable HTTPS/SSL (automatic on most platforms)
- [ ] Restrict CORS to specific origins
- [ ] Enable database backups
- [ ] Set up monitoring/alerts
- [ ] Use environment variables for all secrets
- [ ] Enable rate limiting (already in backend)
- [ ] Keep dependencies updated
- [ ] Use read-only filesystem where possible

---

## 📊 Monitoring & Logging

### Health Check Endpoint
```bash
curl https://your-api.com/api/v1/health
```

### Platform-Specific Monitoring

**Railway:**
```bash
railway logs
railway status
```

**Render:**
- Dashboard → Logs (real-time)
- Metrics tab for performance

**Fly.io:**
```bash
fly logs
fly status
fly dashboard
```

**DigitalOcean:**
```bash
doctl apps logs YOUR_APP_ID --follow
```

**AWS:**
- CloudWatch Logs
- CloudWatch Metrics
- X-Ray for tracing

---

## 🔄 Continuous Deployment

### GitHub Actions (All Platforms)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      # Railway
      - name: Deploy to Railway
        uses: bervProject/railway-deploy@main
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: pixelpirates-backend

      # Or Render (auto-deploys on push)
      # Or Fly.io
      - name: Deploy to Fly.io
        uses: superfly/flyctl-actions@1.3
        with:
          args: deploy
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

---

## 💰 Cost Optimization

### Railway
- Use `railway sleep` to stop during off-hours
- Monitor usage in dashboard

### Render
- Free tier spins down after 15 min inactivity
- Upgrade only when needed

### Fly.io
- Set `auto_stop_machines = true` in fly.toml
- Scales to zero automatically

### AWS
- Use AWS Budgets to set alerts
- Stop RDS instances during development
- Use Reserved Instances for predictable workloads

---

## 🆘 Troubleshooting

### Database Connection Errors
```bash
# Test connection
psql $DATABASE_URL

# Check if backend can reach database
curl https://your-api.com/api/v1/health
```

### Container Won't Start
```bash
# Check logs
railway logs  # or platform-specific command

# Common issues:
# - Missing environment variables
# - Database not ready (increase health check start_period)
# - Port already in use
```

### CORS Errors from Mobile App
- Ensure backend CORS allows your domain
- Check if HTTPS is enabled
- Verify API URL in mobile app is correct

### High Memory Usage
- Reduce uvicorn workers in production
- Enable Redis maxmemory policy
- Monitor with platform tools

---

## 📚 Additional Resources

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [PostgreSQL Connection Pooling](https://www.postgresql.org/docs/current/runtime-config-connection.html)
- [Redis Performance](https://redis.io/docs/management/optimization/)

---

## 🎯 Recommended Path

**For Beginners:** Railway → Render → Fly.io
**For Production:** DigitalOcean or AWS
**For Global Apps:** Fly.io or Google Cloud Run
**For Serverless:** Google Cloud Run or AWS Lambda

---

**Need Help?** Check platform-specific documentation or open an issue!

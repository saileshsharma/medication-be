# Docker Usage Guide

Complete guide for running Pixel Pirates Backend with Docker.

## Quick Start (Development)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down
```

Access:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5433
- Redis: localhost:6380

## Development vs Production

### Development (docker-compose.yml)

**Features:**
- ✅ Hot reload enabled
- ✅ Source code mounted as volume
- ✅ Debug mode on
- ✅ Single worker
- ✅ Verbose logging

**Usage:**
```bash
docker-compose up -d
```

### Production (docker-compose.prod.yml)

**Features:**
- ✅ Optimized multi-stage build
- ✅ Multiple workers (4)
- ✅ No hot reload
- ✅ Production logging
- ✅ Environment variables from .env
- ✅ Automatic restart
- ✅ Log rotation

**Usage:**
```bash
# Copy and configure environment
cp .env.production.example .env.production
# Edit .env.production with your values
nano .env.production

# Start production
docker-compose -f docker-compose.prod.yml up -d
```

## Dockerfile Options

### Dockerfile (Development/Default)

**Best for:**
- Local development
- Testing
- Quick iterations

**Features:**
- Single-stage build
- Includes curl for health checks
- Non-root user (appuser)
- NLTK data pre-downloaded
- Development-friendly

**Build:**
```bash
docker build -t pixelpirates-backend .
```

### Dockerfile.prod (Production)

**Best for:**
- Production deployments
- Cloud hosting
- Performance optimization

**Features:**
- Multi-stage build (smaller image)
- Optimized layers
- 4 uvicorn workers
- Production logging level
- Security hardening

**Build:**
```bash
docker build -f Dockerfile.prod -t pixelpirates-backend:prod .
```

**Size Comparison:**
- Development: ~600-700 MB
- Production: ~500-600 MB (25% smaller)

## Common Commands

### Build & Run

```bash
# Build without cache
docker-compose build --no-cache

# Rebuild and restart
docker-compose up -d --build

# Start specific service
docker-compose up -d backend
```

### Logs & Debugging

```bash
# View all logs
docker-compose logs

# Follow backend logs
docker-compose logs -f backend

# View last 100 lines
docker-compose logs --tail=100 backend

# Check container status
docker-compose ps

# Execute command in container
docker-compose exec backend python -c "import sys; print(sys.version)"
```

### Database Operations

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U postgres -d pixelpirates

# Backup database
docker-compose exec postgres pg_dump -U postgres pixelpirates > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U postgres -d pixelpirates

# View database size
docker-compose exec postgres psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('pixelpirates'));"
```

### Redis Operations

```bash
# Access Redis CLI
docker-compose exec redis redis-cli

# Check keys
docker-compose exec redis redis-cli KEYS "*"

# Flush cache
docker-compose exec redis redis-cli FLUSHDB

# Get info
docker-compose exec redis redis-cli INFO
```

### Health Checks

```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Check container health
docker-compose ps

# Detailed health status
docker inspect pixelpirates-backend | grep -A 10 Health
```

### Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes data!)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Full cleanup
docker system prune -a --volumes
```

## Environment Variables

### Development (.env)

Created automatically from docker-compose.yml.

### Production (.env.production)

Required variables:
```bash
POSTGRES_PASSWORD=strong_password_here
SECRET_KEY=generate_with_openssl_rand_hex_32
GOOGLE_FACT_CHECK_API_KEY=optional
NEWS_API_KEY=optional
```

Generate secret key:
```bash
openssl rand -hex 32
```

## Port Configuration

Default ports (can be changed in .env):

| Service | Dev Port | Prod Port | Container Port |
|---------|----------|-----------|----------------|
| Backend | 8000 | 8000 | 8000 |
| PostgreSQL | 5433 | 5432 | 5432 |
| Redis | 6380 | 6379 | 6379 |

Change ports in docker-compose:
```yaml
ports:
  - "CUSTOM_PORT:8000"
```

## Volumes

### Development
```yaml
volumes:
  - .:/app  # Source code mounted
```

### Production
```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
  - redis_data:/data
```

View volumes:
```bash
docker volume ls
docker volume inspect pixelpirates-backend_postgres_data
```

## Network Configuration

Default network: `bridge`

Production network: `pixelpirates-network`

Connect to network:
```bash
docker network inspect pixelpirates-backend_default
```

## Performance Tuning

### Workers

Development: 1 worker (easier debugging)
Production: 4 workers (better performance)

Change in CMD:
```dockerfile
CMD ["uvicorn", "main:app", "--workers", "4"]
```

### Resource Limits

Add to docker-compose.yml:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 1G
```

### Database Connection Pool

Adjust in backend code:
```python
pool_size=10
max_overflow=20
```

## Security Best Practices

### ✅ Implemented

- Non-root user (appuser)
- Read-only root filesystem (optional)
- No privileged mode
- Health checks
- Secrets via environment variables
- Multi-stage builds

### 🔒 Recommended

1. **Use secrets management:**
   ```bash
   docker secret create db_password password.txt
   ```

2. **Scan images:**
   ```bash
   docker scan pixelpirates-backend
   ```

3. **Update regularly:**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

4. **Enable firewall:**
   ```bash
   # Only expose what's needed
   ports:
     - "127.0.0.1:8000:8000"  # Localhost only
   ```

## Troubleshooting

### Port Already in Use

```bash
# Find what's using port
lsof -i :5432

# Change port in docker-compose.yml
ports:
  - "5434:5432"
```

### Permission Denied

```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Rebuild without cache
docker-compose build --no-cache
```

### Container Crashes

```bash
# View logs
docker-compose logs backend

# Check health
docker-compose ps

# Restart
docker-compose restart backend
```

### Database Connection Error

```bash
# Check postgres is healthy
docker-compose ps postgres

# Check connection string
docker-compose exec backend env | grep DATABASE_URL

# Test connection
docker-compose exec backend python -c "from app.db.database import engine; print(engine.execute('SELECT 1').scalar())"
```

### Out of Memory

```bash
# Check usage
docker stats

# Increase limit
docker-compose up -d --memory="2g"
```

## Production Deployment Checklist

- [ ] Copy `.env.production.example` to `.env.production`
- [ ] Generate strong `SECRET_KEY`
- [ ] Set strong `POSTGRES_PASSWORD`
- [ ] Set `DEBUG=False`
- [ ] Configure API keys (optional)
- [ ] Review resource limits
- [ ] Set up SSL/TLS (use nginx reverse proxy)
- [ ] Configure backups
- [ ] Set up monitoring
- [ ] Configure log aggregation
- [ ] Test health checks
- [ ] Document deployment process

## Backup & Restore

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U postgres pixelpirates > "backup_$DATE.sql"
echo "Backup created: backup_$DATE.sql"
```

### Restore from Backup

```bash
cat backup_20250108_120000.sql | docker-compose exec -T postgres psql -U postgres -d pixelpirates
```

## Monitoring

### Container Stats

```bash
# Real-time stats
docker stats pixelpirates-backend

# One-time stats
docker stats --no-stream
```

### Application Metrics

Available at: `http://localhost:8000/api/v1/cache/stats`

### Log Aggregation

For production, use:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Grafana + Loki
- CloudWatch (AWS)
- Stackdriver (GCP)

## Update Strategy

### Development

```bash
git pull
docker-compose down
docker-compose up -d --build
```

### Production

```bash
# Backup first!
./backup.sh

# Pull latest
git pull

# Rebuild
docker-compose -f docker-compose.prod.yml build

# Zero-downtime update (if using multiple instances)
docker-compose -f docker-compose.prod.yml up -d --no-deps --build backend
```

## Support

- Docker Documentation: https://docs.docker.com
- Docker Compose Reference: https://docs.docker.com/compose/compose-file/
- FastAPI in Docker: https://fastapi.tiangolo.com/deployment/docker/

---

**Ready to deploy!** 🚀

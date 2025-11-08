# Pixel Pirates Backend - Quick Start Guide

Get the backend running in under 5 minutes!

## Prerequisites

- Docker & Docker Compose (easiest)
- OR Python 3.11+, PostgreSQL, and Redis (manual setup)

## Option 1: Docker (Recommended) ⚡

### 1. Start the Backend

```bash
cd pixel-pirates-backend
docker-compose up -d
```

That's it! The backend will be running at http://localhost:8000

### 2. Verify It's Working

Open http://localhost:8000/docs in your browser. You should see the interactive API documentation.

### 3. Test the API

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Breaking news: Scientists discover cure for aging!",
    "content_type": "text",
    "source_app": "Test"
  }'
```

### 4. View Logs

```bash
docker-compose logs -f backend
```

### 5. Stop the Backend

```bash
docker-compose down
```

## Option 2: Manual Setup (Development) 🛠️

### 1. Install Dependencies

```bash
# Install Python dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install PostgreSQL
brew install postgresql  # macOS
sudo apt install postgresql  # Ubuntu

# Install Redis
brew install redis  # macOS
sudo apt install redis-server  # Ubuntu
```

### 2. Start Services

```bash
# Start PostgreSQL
brew services start postgresql  # macOS
sudo service postgresql start  # Ubuntu

# Start Redis
brew services start redis  # macOS
sudo service redis-server start  # Ubuntu

# Create database
createdb pixelpirates
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env if needed (default values should work)
```

### 4. Run the Backend

```bash
python main.py
```

## Testing the API

### 1. Check Health

```bash
curl http://localhost:8000/api/v1/health
```

### 2. Analyze Content

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Climate summit agrees on historic deal to reduce carbon emissions",
    "content_type": "text"
  }'
```

### 3. View Documentation

Open your browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Connecting to Mobile App

Update your React Native app's API configuration:

```typescript
// For iOS Simulator
const API_URL = 'http://localhost:8000/api/v1';

// For Android Emulator
const API_URL = 'http://10.0.2.2:8000/api/v1';

// For Physical Device (use your computer's IP)
const API_URL = 'http://192.168.1.XXX:8000/api/v1';
```

## Common Issues

### Port Already in Use

```bash
# Find what's using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

### Database Connection Error

```bash
# Check PostgreSQL is running
pg_isready
# If not, start it
brew services start postgresql
```

### Redis Connection Error

```bash
# Check Redis is running
redis-cli ping
# Should return PONG
# If not, start it
brew services start redis
```

## Next Steps

1. ✅ Backend is running
2. ✅ API is accessible
3. ✅ Documentation is available
4. 📱 Update mobile app to use backend
5. 🚀 Deploy to production

See README.md for full documentation!

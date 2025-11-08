#!/bin/bash

# Pixel Pirates Backend - Quick Start Script

echo "🏴‍☠️ Pixel Pirates Backend - Starting..."

# Check if Docker is installed
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose found"
    echo "🚀 Starting services with Docker..."

    # Create .env if it doesn't exist
    if [ ! -f .env ]; then
        echo "📝 Creating .env from .env.example..."
        cp .env.example .env
    fi

    # Start services
    docker-compose up -d

    echo ""
    echo "⏳ Waiting for services to be ready..."
    sleep 5

    # Check health
    if curl -s http://localhost:8000/api/v1/health > /dev/null; then
        echo "✅ Backend is running!"
        echo ""
        echo "📚 API Documentation: http://localhost:8000/docs"
        echo "🔍 ReDoc: http://localhost:8000/redoc"
        echo "💚 Health Check: http://localhost:8000/api/v1/health"
        echo ""
        echo "📊 View logs: docker-compose logs -f backend"
        echo "🛑 Stop: docker-compose down"
    else
        echo "❌ Backend failed to start"
        echo "📊 Check logs: docker-compose logs backend"
        exit 1
    fi

else
    echo "❌ Docker Compose not found"
    echo ""
    echo "Please install Docker Desktop from:"
    echo "https://www.docker.com/products/docker-desktop"
    echo ""
    echo "Or run manually:"
    echo "1. Install PostgreSQL and Redis"
    echo "2. pip install -r requirements.txt"
    echo "3. python main.py"
    exit 1
fi

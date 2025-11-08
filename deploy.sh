#!/bin/bash

# Pixel Pirates Backend - Deployment Script
# Quick deployment to various cloud platforms

set -e

echo "🏴‍☠️ Pixel Pirates Backend - Deployment Tool"
echo "============================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if required tools are installed
check_requirement() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}✗ $1 is not installed${NC}"
        return 1
    else
        echo -e "${GREEN}✓ $1 is installed${NC}"
        return 0
    fi
}

# Platform selection
echo "Select deployment platform:"
echo "1) Railway (Recommended for beginners)"
echo "2) Render"
echo "3) Fly.io"
echo "4) DigitalOcean"
echo "5) Docker Production Build (Local)"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo -e "\n${BLUE}Deploying to Railway...${NC}\n"

        # Check requirements
        if ! check_requirement "railway"; then
            echo -e "\n${YELLOW}Installing Railway CLI...${NC}"
            npm i -g @railway/cli
        fi

        # Check git
        if [ ! -d .git ]; then
            echo -e "\n${YELLOW}Initializing git repository...${NC}"
            git init
            git add .
            git commit -m "Initial commit - Ready for deployment"
        fi

        # Deploy
        echo -e "\n${YELLOW}Initializing Railway project...${NC}"
        railway init

        echo -e "\n${YELLOW}Adding PostgreSQL...${NC}"
        railway add --database postgres

        echo -e "\n${YELLOW}Adding Redis...${NC}"
        railway add --database redis

        echo -e "\n${YELLOW}Setting environment variables...${NC}"
        SECRET_KEY=$(openssl rand -hex 32)
        railway variables set SECRET_KEY=$SECRET_KEY
        railway variables set DEBUG=False
        railway variables set ENVIRONMENT=production

        echo -e "\n${YELLOW}Deploying application...${NC}"
        railway up

        echo -e "\n${GREEN}✓ Deployment complete!${NC}"
        echo -e "\n${BLUE}Getting your app URL...${NC}"
        railway domain

        echo -e "\n${GREEN}Test your deployment:${NC}"
        echo "curl https://your-app.railway.app/api/v1/health"
        ;;

    2)
        echo -e "\n${BLUE}Deploying to Render...${NC}\n"

        # Check git
        if [ ! -d .git ]; then
            echo -e "\n${YELLOW}Initializing git repository...${NC}"
            git init
            git add .
            git commit -m "Initial commit - Ready for deployment"
        fi

        echo -e "\n${YELLOW}render.yaml file is ready in your repo${NC}"
        echo -e "\n${GREEN}Next steps:${NC}"
        echo "1. Push to GitHub: git push origin main"
        echo "2. Go to https://render.com"
        echo "3. Click 'New +' → 'Blueprint'"
        echo "4. Connect your GitHub repo"
        echo "5. Render will auto-detect render.yaml and deploy!"
        echo ""
        echo -e "${YELLOW}Don't forget to set these secrets in Render dashboard:${NC}"
        SECRET_KEY=$(openssl rand -hex 32)
        echo "SECRET_KEY=$SECRET_KEY"
        echo "GOOGLE_FACT_CHECK_API_KEY=your_key_here (optional)"
        echo "NEWS_API_KEY=your_key_here (optional)"
        ;;

    3)
        echo -e "\n${BLUE}Deploying to Fly.io...${NC}\n"

        # Check requirements
        if ! check_requirement "flyctl"; then
            echo -e "\n${YELLOW}Installing Fly CLI...${NC}"
            curl -L https://fly.io/install.sh | sh
            echo -e "\n${RED}Please add flyctl to your PATH and run this script again${NC}"
            exit 1
        fi

        # Login
        echo -e "\n${YELLOW}Logging in to Fly.io...${NC}"
        fly auth login

        # Launch
        echo -e "\n${YELLOW}Launching app (don't deploy yet)...${NC}"
        fly launch --no-deploy

        # Create databases
        echo -e "\n${YELLOW}Creating PostgreSQL database...${NC}"
        fly postgres create --name pixelpirates-db
        fly postgres attach pixelpirates-db

        echo -e "\n${YELLOW}Creating Redis...${NC}"
        fly redis create

        # Set secrets
        echo -e "\n${YELLOW}Setting secrets...${NC}"
        SECRET_KEY=$(openssl rand -hex 32)
        fly secrets set SECRET_KEY=$SECRET_KEY

        read -p "Enter GOOGLE_FACT_CHECK_API_KEY (or press Enter to skip): " GOOGLE_KEY
        if [ ! -z "$GOOGLE_KEY" ]; then
            fly secrets set GOOGLE_FACT_CHECK_API_KEY=$GOOGLE_KEY
        fi

        read -p "Enter NEWS_API_KEY (or press Enter to skip): " NEWS_KEY
        if [ ! -z "$NEWS_KEY" ]; then
            fly secrets set NEWS_API_KEY=$NEWS_KEY
        fi

        # Deploy
        echo -e "\n${YELLOW}Deploying to Fly.io...${NC}"
        fly deploy

        echo -e "\n${GREEN}✓ Deployment complete!${NC}"
        echo -e "\n${BLUE}Opening your app...${NC}"
        fly open /api/v1/health
        ;;

    4)
        echo -e "\n${BLUE}Deploying to DigitalOcean...${NC}\n"

        # Check requirements
        if ! check_requirement "doctl"; then
            echo -e "\n${RED}Please install doctl first:${NC}"
            echo "macOS: brew install doctl"
            echo "Linux: https://docs.digitalocean.com/reference/doctl/how-to/install/"
            exit 1
        fi

        # Check authentication
        echo -e "\n${YELLOW}Checking authentication...${NC}"
        if ! doctl account get &> /dev/null; then
            echo -e "\n${YELLOW}Please authenticate with DigitalOcean...${NC}"
            doctl auth init
        fi

        # Update app.yaml
        echo -e "\n${YELLOW}Make sure to update .do/app.yaml with your GitHub repo${NC}"
        read -p "Press Enter when ready to continue..."

        # Create app
        echo -e "\n${YELLOW}Creating app on DigitalOcean...${NC}"
        doctl apps create --spec .do/app.yaml

        echo -e "\n${GREEN}✓ App created!${NC}"
        echo -e "\n${YELLOW}Don't forget to:${NC}"
        echo "1. Set SECRET_KEY in DigitalOcean dashboard"
        SECRET_KEY=$(openssl rand -hex 32)
        echo "   SECRET_KEY=$SECRET_KEY"
        echo "2. Add API keys (optional)"
        echo "3. Connect databases in dashboard"
        ;;

    5)
        echo -e "\n${BLUE}Building Docker Production Image...${NC}\n"

        # Check Docker
        if ! check_requirement "docker"; then
            echo -e "\n${RED}Docker is not installed. Please install Docker first.${NC}"
            exit 1
        fi

        # Build
        echo -e "\n${YELLOW}Building production image...${NC}"
        docker build -f Dockerfile.prod -t pixelpirates-backend:prod .

        # Create .env.production if not exists
        if [ ! -f .env.production ]; then
            echo -e "\n${YELLOW}Creating .env.production file...${NC}"
            cp .env.production.example .env.production
            SECRET_KEY=$(openssl rand -hex 32)
            sed -i.bak "s/GENERATE_A_STRONG_RANDOM_SECRET_KEY_HERE/$SECRET_KEY/" .env.production
            sed -i.bak "s/CHANGE_ME_IN_PRODUCTION/$(openssl rand -base64 32)/" .env.production
            rm .env.production.bak
            echo -e "${GREEN}✓ Created .env.production${NC}"
            echo -e "${YELLOW}Please review and update .env.production with your values${NC}"
        fi

        # Start production
        echo -e "\n${YELLOW}Starting production containers...${NC}"
        docker-compose -f docker-compose.prod.yml up -d

        echo -e "\n${GREEN}✓ Production build complete!${NC}"
        echo -e "\n${BLUE}Checking health...${NC}"
        sleep 5
        curl http://localhost:8000/api/v1/health || echo -e "${RED}Health check failed${NC}"

        echo -e "\n${GREEN}Production is running!${NC}"
        echo "API: http://localhost:8000"
        echo "Docs: http://localhost:8000/docs"
        echo ""
        echo "View logs: docker-compose -f docker-compose.prod.yml logs -f"
        echo "Stop: docker-compose -f docker-compose.prod.yml down"
        ;;

    *)
        echo -e "\n${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 Deployment process complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Test your API health endpoint"
echo "2. Update mobile app with production URL"
echo "3. Set up monitoring and alerts"
echo "4. Configure custom domain (optional)"
echo ""
echo -e "${YELLOW}For detailed instructions, see DEPLOYMENT.md${NC}"

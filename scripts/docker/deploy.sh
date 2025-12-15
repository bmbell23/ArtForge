#!/bin/bash
set -e

# ArtForge Docker Deployment Script
# Usage: ./scripts/docker/deploy.sh [--env dev|prod] [--build]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Default values
ENVIRONMENT="dev"
BUILD_FIRST=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --build)
            BUILD_FIRST=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--env dev|prod] [--build]"
            echo "  --env    Environment to deploy (dev or prod, default: dev)"
            echo "  --build  Build image before deploying"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

cd "$PROJECT_ROOT"

echo "🚀 Deploying ArtForge..."
echo "Environment: $ENVIRONMENT"

# Determine compose file
if [[ "$ENVIRONMENT" == "prod" ]]; then
    COMPOSE_FILE="docker-compose.prod.yml"
else
    COMPOSE_FILE="docker-compose.dev.yml"
fi

# Build if requested
if [[ "$BUILD_FIRST" == true ]]; then
    echo "🏗️  Building first..."
    ./scripts/docker/build.sh --env "$ENVIRONMENT"
fi

# Create necessary directories
mkdir -p data/uploads

# Deploy
echo "📦 Starting services with $COMPOSE_FILE..."
docker-compose -f "$COMPOSE_FILE" up -d

echo "✅ ArtForge deployed successfully!"
echo ""
echo "🌐 Application URLs:"
if [[ "$ENVIRONMENT" == "prod" ]]; then
    echo "   Production: http://localhost (via nginx)"
    echo "   Direct: http://localhost:8003"
else
    echo "   Development: http://localhost:8003"
    echo "   Local network: http://$(hostname -I | awk '{print $1}'):8003"
fi
echo ""
echo "🔧 Management commands:"
echo "   ./scripts/docker/manage.sh logs    # View logs"
echo "   ./scripts/docker/manage.sh stop    # Stop services"
echo "   ./scripts/docker/manage.sh shell   # Access container shell"

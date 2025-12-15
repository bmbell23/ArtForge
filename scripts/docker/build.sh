#!/bin/bash
set -e

# ArtForge Docker Build Script
# Usage: ./scripts/docker/build.sh [--env dev|prod] [--force]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Default values
ENVIRONMENT="dev"
FORCE_BUILD=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --force)
            FORCE_BUILD=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--env dev|prod] [--force]"
            echo "  --env    Environment to build for (dev or prod, default: dev)"
            echo "  --force  Force rebuild without cache"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

cd "$PROJECT_ROOT"

echo "🏗️  Building ArtForge Docker image..."
echo "Environment: $ENVIRONMENT"
echo "Project root: $PROJECT_ROOT"

# Determine compose file and target
if [[ "$ENVIRONMENT" == "prod" ]]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    TARGET="production"
else
    COMPOSE_FILE="docker-compose.dev.yml"
    TARGET="development"
fi

# Build arguments
BUILD_ARGS=""
if [[ "$FORCE_BUILD" == true ]]; then
    BUILD_ARGS="--no-cache"
fi

echo "📦 Building with target: $TARGET"
echo "📄 Using compose file: $COMPOSE_FILE"

# Build the image
docker-compose -f "$COMPOSE_FILE" build $BUILD_ARGS

echo "✅ ArtForge Docker image built successfully!"
echo ""
echo "🚀 To start the application:"
echo "   ./scripts/docker/deploy.sh --env $ENVIRONMENT"
echo ""
echo "🔧 To manage the application:"
echo "   ./scripts/docker/manage.sh --help"

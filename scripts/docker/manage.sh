#!/bin/bash
set -e

# ArtForge Docker Management Script
# Usage: ./scripts/docker/manage.sh <command> [options]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Default environment
ENVIRONMENT="dev"

show_help() {
    echo "ArtForge Docker Management"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  start [--env dev|prod]     Start the application"
    echo "  stop [--env dev|prod]      Stop the application"
    echo "  restart [--env dev|prod]   Restart the application"
    echo "  logs [--env dev|prod]      Show application logs"
    echo "  shell [--env dev|prod]     Access container shell"
    echo "  status [--env dev|prod]    Show container status"
    echo "  clean                      Remove containers and images"
    echo "  db-backup                  Backup database"
    echo "  db-restore <file>          Restore database from backup"
    echo ""
    echo "Options:"
    echo "  --env    Environment (dev or prod, default: dev)"
    echo "  -h, --help    Show this help message"
}

# Parse environment option
parse_env_option() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            *)
                break
                ;;
        esac
    done
}

get_compose_file() {
    if [[ "$ENVIRONMENT" == "prod" ]]; then
        echo "docker-compose.prod.yml"
    else
        echo "docker-compose.dev.yml"
    fi
}

cd "$PROJECT_ROOT"

# Parse command
COMMAND="$1"
shift || true

case "$COMMAND" in
    start)
        parse_env_option "$@"
        COMPOSE_FILE=$(get_compose_file)
        echo "🚀 Starting ArtForge ($ENVIRONMENT)..."
        docker-compose -f "$COMPOSE_FILE" up -d
        echo "✅ ArtForge started!"
        ;;
    stop)
        parse_env_option "$@"
        COMPOSE_FILE=$(get_compose_file)
        echo "🛑 Stopping ArtForge ($ENVIRONMENT)..."
        docker-compose -f "$COMPOSE_FILE" down
        echo "✅ ArtForge stopped!"
        ;;
    restart)
        parse_env_option "$@"
        COMPOSE_FILE=$(get_compose_file)
        echo "🔄 Restarting ArtForge ($ENVIRONMENT)..."
        docker-compose -f "$COMPOSE_FILE" restart
        echo "✅ ArtForge restarted!"
        ;;
    logs)
        parse_env_option "$@"
        COMPOSE_FILE=$(get_compose_file)
        docker-compose -f "$COMPOSE_FILE" logs -f
        ;;
    shell)
        parse_env_option "$@"
        if [[ "$ENVIRONMENT" == "prod" ]]; then
            CONTAINER="artforge-prod"
        else
            CONTAINER="artforge-dev"
        fi
        echo "🐚 Accessing $CONTAINER shell..."
        docker exec -it "$CONTAINER" /bin/bash
        ;;
    status)
        parse_env_option "$@"
        COMPOSE_FILE=$(get_compose_file)
        docker-compose -f "$COMPOSE_FILE" ps
        ;;
    clean)
        echo "🧹 Cleaning up ArtForge containers and images..."
        docker-compose -f docker-compose.dev.yml down --rmi all --volumes --remove-orphans 2>/dev/null || true
        docker-compose -f docker-compose.prod.yml down --rmi all --volumes --remove-orphans 2>/dev/null || true
        echo "✅ Cleanup complete!"
        ;;
    db-backup)
        BACKUP_FILE="data/art_forge_backup_$(date +%Y%m%d_%H%M%S).db"
        echo "💾 Backing up database to $BACKUP_FILE..."
        cp data/art_forge.db "$BACKUP_FILE"
        echo "✅ Database backed up to $BACKUP_FILE"
        ;;
    db-restore)
        RESTORE_FILE="$1"
        if [[ -z "$RESTORE_FILE" ]]; then
            echo "❌ Please specify backup file to restore"
            exit 1
        fi
        if [[ ! -f "$RESTORE_FILE" ]]; then
            echo "❌ Backup file not found: $RESTORE_FILE"
            exit 1
        fi
        echo "📥 Restoring database from $RESTORE_FILE..."
        cp "$RESTORE_FILE" data/art_forge.db
        echo "✅ Database restored from $RESTORE_FILE"
        ;;
    -h|--help|help)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        echo ""
        show_help
        exit 1
        ;;
esac

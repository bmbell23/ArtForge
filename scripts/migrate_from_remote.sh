#!/bin/bash
set -e

# ArtForge Migration Script
# Migrates data from remote server (5.78.41.92) to local Docker environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Remote server details
REMOTE_HOST="5.78.41.92"
REMOTE_USER="brandon"
REMOTE_PROJECT_PATH="~/projects/art_gallery"
REMOTE_DB_PATH="$REMOTE_PROJECT_PATH/art_forge.db"
REMOTE_UPLOADS_PATH="$REMOTE_PROJECT_PATH/data/uploads"

# Local paths
LOCAL_DATA_DIR="$PROJECT_ROOT/data"
LOCAL_DB_PATH="$LOCAL_DATA_DIR/art_forge.db"
LOCAL_UPLOADS_DIR="$LOCAL_DATA_DIR/uploads"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if this is a dry run
DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    log_info "Running in DRY RUN mode - no files will be transferred"
fi

log_info "🎨 Starting ArtForge migration from remote server..."
log_info "Remote: $REMOTE_USER@$REMOTE_HOST:$REMOTE_PROJECT_PATH"
log_info "Local: $PROJECT_ROOT"

# Create local directories
log_info "📁 Creating local directories..."
if [[ "$DRY_RUN" == false ]]; then
    mkdir -p "$LOCAL_DATA_DIR"
    mkdir -p "$LOCAL_UPLOADS_DIR"
fi

# Test SSH connection
log_info "🔐 Testing SSH connection to remote server..."
if ! ssh -o ConnectTimeout=10 "$REMOTE_USER@$REMOTE_HOST" "echo 'SSH connection successful'" >/dev/null 2>&1; then
    log_error "Cannot connect to remote server $REMOTE_HOST"
    log_error "Please ensure:"
    log_error "1. SSH key is set up for $REMOTE_USER@$REMOTE_HOST"
    log_error "2. Remote server is accessible"
    exit 1
fi
log_success "SSH connection established"

# Check if remote database exists
log_info "🔍 Checking for remote database..."
if ssh "$REMOTE_USER@$REMOTE_HOST" "test -f $REMOTE_DB_PATH"; then
    DB_SIZE=$(ssh "$REMOTE_USER@$REMOTE_HOST" "stat -f%z $REMOTE_DB_PATH 2>/dev/null || stat -c%s $REMOTE_DB_PATH 2>/dev/null")
    log_success "Found remote database: $REMOTE_DB_PATH ($DB_SIZE bytes)"
    
    if [[ "$DRY_RUN" == false ]]; then
        log_info "📥 Downloading database..."
        scp "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DB_PATH" "$LOCAL_DB_PATH"
        log_success "Database downloaded successfully"
    else
        log_info "[DRY RUN] Would download database from $REMOTE_DB_PATH"
    fi
else
    log_warning "Remote database not found at $REMOTE_DB_PATH"
    log_info "Will create empty database on first run"
fi

# Check for uploads directory
log_info "🖼️  Checking for remote uploads..."
if ssh "$REMOTE_USER@$REMOTE_HOST" "test -d $REMOTE_UPLOADS_PATH"; then
    UPLOAD_COUNT=$(ssh "$REMOTE_USER@$REMOTE_HOST" "find $REMOTE_UPLOADS_PATH -type f | wc -l")
    UPLOAD_SIZE=$(ssh "$REMOTE_USER@$REMOTE_HOST" "du -sh $REMOTE_UPLOADS_PATH | cut -f1")
    log_success "Found remote uploads directory: $UPLOAD_COUNT files ($UPLOAD_SIZE)"
    
    if [[ "$DRY_RUN" == false ]]; then
        log_info "📥 Downloading uploads..."
        rsync -avz --progress "$REMOTE_USER@$REMOTE_HOST:$REMOTE_UPLOADS_PATH/" "$LOCAL_UPLOADS_DIR/"
        log_success "Uploads downloaded successfully"
    else
        log_info "[DRY RUN] Would download uploads from $REMOTE_UPLOADS_PATH"
    fi
else
    log_warning "Remote uploads directory not found at $REMOTE_UPLOADS_PATH"
    log_info "Will create empty uploads directory"
fi

if [[ "$DRY_RUN" == false ]]; then
    log_success "🎉 ArtForge migration completed successfully!"
    log_info ""
    log_info "📊 Migration Summary:"
    if [[ -f "$LOCAL_DB_PATH" ]]; then
        LOCAL_DB_SIZE=$(stat -f%z "$LOCAL_DB_PATH" 2>/dev/null || stat -c%s "$LOCAL_DB_PATH" 2>/dev/null)
        log_info "  Database: $LOCAL_DB_SIZE bytes"
    fi
    if [[ -d "$LOCAL_UPLOADS_DIR" ]]; then
        LOCAL_UPLOAD_COUNT=$(find "$LOCAL_UPLOADS_DIR" -type f | wc -l)
        LOCAL_UPLOAD_SIZE=$(du -sh "$LOCAL_UPLOADS_DIR" | cut -f1)
        log_info "  Uploads: $LOCAL_UPLOAD_COUNT files ($LOCAL_UPLOAD_SIZE)"
    fi
    log_info ""
    log_info "🚀 Next steps:"
    log_info "1. Build and start the Docker container:"
    log_info "   ./scripts/docker/build.sh --env dev"
    log_info "   ./scripts/docker/deploy.sh --env dev"
    log_info "2. Access the application at http://localhost:8003"
else
    log_info "🔍 DRY RUN completed - no files were transferred"
fi

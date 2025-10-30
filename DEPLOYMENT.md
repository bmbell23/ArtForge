# ArtForge Deployment Guide

## 🎉 Successfully Deployed!

**Live URL**: https://forge-freedom.com/art/

## Architecture

- **Application**: FastAPI (Python)
- **Port**: 8003
- **Database**: SQLite (`art_forge.db`)
- **Static Files**: Served under `/art/static/`
- **Uploads**: Served under `/art/uploads/`
- **Auth Routes**: `/art/login`, `/art/register`, `/art/logout`
- **Service**: systemd (`art-forge.service`)
- **Reverse Proxy**: nginx

### Important: Path Namespacing

All ArtForge routes are namespaced under `/art/` to avoid conflicts with other applications on the same domain (e.g., WordForge at `/writing/`). This includes:
- Static files: `/art/static/css/style.css`
- Uploads: `/art/uploads/image.jpg`
- Auth routes: `/art/login`, `/art/register`, `/art/logout`
- User galleries: `/art/{username}`

## Service Management

### Start/Stop/Restart
```bash
sudo systemctl start art-forge
sudo systemctl stop art-forge
sudo systemctl restart art-forge
sudo systemctl status art-forge
```

### View Logs
```bash
# Real-time logs
sudo journalctl -u art-forge -f

# Recent logs
sudo journalctl -u art-forge -n 100

# Nginx access logs
sudo tail -f /var/log/nginx/forge-freedom-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/forge-freedom-error.log
```

## Nginx Configuration

The nginx configuration is in `/etc/nginx/sites-available/forge-freedom.conf`

Key locations:
- `/art/` - Main application proxy to port 8003
- `/art/static/` - Static files (CSS, JS)
- `/art/uploads/` - User-uploaded images

### Reload Nginx
```bash
# Test configuration
sudo nginx -t

# Reload (no downtime)
sudo systemctl reload nginx

# Restart (brief downtime)
sudo systemctl restart nginx
```

## File Locations

- **Project**: `/home/brandon/projects/art_gallery/`
- **Virtual Environment**: `/home/brandon/projects/art_gallery/venv/`
- **Database**: `/home/brandon/projects/art_gallery/art_forge.db`
- **Uploads**: `/home/brandon/projects/art_gallery/data/uploads/`
- **Service File**: `/etc/systemd/system/art-forge.service`
- **Nginx Config**: `/etc/nginx/sites-available/forge-freedom.conf`

## Database Management

### Backup Database
```bash
cd /home/brandon/projects/art_gallery
cp art_forge.db art_forge.db.backup-$(date +%Y%m%d-%H%M%S)
```

### Run Migrations
```bash
cd /home/brandon/projects/art_gallery
source venv/bin/activate
alembic upgrade head
```

### Create New Migration
```bash
cd /home/brandon/projects/art_gallery
source venv/bin/activate
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## Troubleshooting

### Service Won't Start
```bash
# Check service status
sudo systemctl status art-forge

# Check logs
sudo journalctl -u art-forge -n 50

# Check if port is in use
sudo lsof -i :8003
```

### CSS Not Loading
- Verify static files are at `/home/brandon/projects/art_gallery/src/art_forge/static/`
- Check nginx is proxying `/art/static/` correctly
- Clear browser cache

### Images Not Displaying
- Verify uploads directory exists: `/home/brandon/projects/art_gallery/data/uploads/`
- Check file permissions: `ls -la data/uploads/`
- Verify nginx is proxying `/art/uploads/` correctly

### Database Issues
```bash
# Check database file exists
ls -lh art_forge.db

# Check database integrity
sqlite3 art_forge.db "PRAGMA integrity_check;"

# View tables
sqlite3 art_forge.db ".tables"
```

## Updates and Maintenance

### Update Code
```bash
cd /home/brandon/projects/art_gallery
git pull  # if using git
sudo systemctl restart art-forge
```

### Update Dependencies
```bash
cd /home/brandon/projects/art_gallery
source venv/bin/activate
pip install --upgrade -r requirements.txt  # if you create one
# OR
pip install -e .
sudo systemctl restart art-forge
```

## Security Notes

- Database credentials are in `.env` file (not committed to git)
- JWT secret key is in `.env` file
- Uploaded images are stored in `data/uploads/` (excluded from git)
- SSL/TLS handled by nginx with Let's Encrypt certificates

## Features Implemented (MVP)

✅ User authentication (register/login/logout)
✅ Artwork upload (single/multiple images)
✅ Gallery view
✅ Artwork detail pages
✅ Image protection (no right-click)
✅ Modern, colorful design (purple/pink gradients)
✅ Responsive layout

## Future Features (Database Ready)

- ✨ Sparks (likes/kudos)
- 💬 Comments
- 🏷️ Tags
- 📚 Series

## Health Check

```bash
# Check if service is running
curl https://forge-freedom.com/health

# Should return:
# {"status":"healthy","version":"0.1.0"}
```


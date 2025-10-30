# ArtForge

A modern platform for artists to showcase and share their artwork.

## Features

### MVP (Phase 1)
- 🎨 Upload and showcase artwork
- 🖼️ Multiple images per artwork project
- 👤 User authentication
- 🔗 Shareable links to artworks
- 🔒 Image protection (no right-click download)

### Next Phase
- ✨ Spark system (likes/kudos)
- 💬 Comments on artworks
- 🏷️ Tags and series organization

## Tech Stack

- **Backend**: Python 3.8+ with FastAPI
- **Database**: SQLAlchemy with SQLite (upgradeable to PostgreSQL)
- **Frontend**: Jinja2 templates + Modern CSS
- **Image Processing**: Pillow

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

4. Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   ```

5. Initialize the database:
   ```bash
   alembic upgrade head
   ```

6. Create upload directory:
   ```bash
   mkdir -p data/uploads
   ```

7. Run the development server:
   ```bash
   uvicorn art_forge.main:app --reload --port 8003
   ```

## Deployment

The application can be deployed as a systemd service:

1. Copy the service file:
   ```bash
   sudo cp art-forge.service /etc/systemd/system/
   ```

2. Enable and start the service:
   ```bash
   sudo systemctl enable art-forge
   sudo systemctl start art-forge
   ```

## URL Structure

- `/art/` - Main landing page
- `/art/{username}` - User's artwork gallery
- `/art/{username}/upload` - Upload new artwork
- `/art/{username}/{slug}` - View specific artwork

## License

Private project


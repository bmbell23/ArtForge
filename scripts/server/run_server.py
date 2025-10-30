#!/usr/bin/env python3
"""Run the ArtForge server."""

import uvicorn
from art_forge.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "art_forge.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level="info"
    )


# Multi-stage build for ArtForge
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy source code first
COPY . .

# Install the package
RUN pip install --no-cache-dir -e .

# Development stage
FROM base as development

# Copy source code
COPY . .

# Install the package with development dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Create necessary directories
RUN mkdir -p /app/data/uploads

# Expose port
EXPOSE 8003

# Command for development
CMD ["python", "-m", "uvicorn", "art_forge.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]

# Production stage
FROM base as production

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/uploads

# Create non-root user
RUN useradd --create-home --shell /bin/bash artforge
RUN chown -R artforge:artforge /app
USER artforge

# Expose port
EXPOSE 8003

# Command for production
CMD ["python", "-m", "uvicorn", "art_forge.main:app", "--host", "0.0.0.0", "--port", "8003"]

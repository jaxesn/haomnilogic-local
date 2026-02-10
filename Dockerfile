# Multi-stage build for haomnilogic-local
# Stage 1: Builder
FROM python:3.13-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/

# Copy project files for dependency resolution
COPY pyproject.toml uv.lock ./

# Regenerate the lockfile inside the container to resolve the git source
# This ensures we always pull the latest from the branch during build
RUN /uv/bin/uv lock --upgrade-package python-omnilogic-local

# Synchronize dependencies exactly as defined in the newly generated lockfile
RUN /uv/bin/uv sync --no-dev --no-install-project

# Copy the actual project code and install the package itself
COPY . .
RUN /uv/bin/uv sync --no-dev

# Stage 2: Runtime
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies for scapy
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire working directory and virtual environment
COPY --from=builder /app /app

# Set environment variables to use the uv-created virtual environment
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Create non-root user for security
RUN useradd -m -u 1000 omnilogic && \
    chown -R omnilogic:omnilogic /app

USER omnilogic

# Set entrypoint to the omnilogic CLI (provided by the library dependency)
ENTRYPOINT ["omnilogic"]

# Default help command
CMD ["--help"]

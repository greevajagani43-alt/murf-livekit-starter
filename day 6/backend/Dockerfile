# ─────────────────────────────────────────────────────────────────────────────
# Day 6 Backend Dockerfile
# Builds the Saathi outbound voice agent
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files first (layer caching)
COPY pyproject.toml .
COPY src/ src/

# Install dependencies
RUN uv sync --no-dev

# Copy remaining files
COPY data/ data/
COPY .env.example .

# Download LiveKit model files at build time
RUN uv run python src/agent.py download-files

EXPOSE 8080

CMD ["uv", "run", "python", "src/agent.py", "start"]

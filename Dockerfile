FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/

# Accept build args and set as ENV
ARG OPENAI_API_KEY
ARG ELEVENLABS_API_KEY
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}

# Expose port
EXPOSE 8001

# Ensure no .env file is loaded (use ENV variables only)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Health check (using curl instead of requests)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Run application (single worker to avoid ENV cache issues)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

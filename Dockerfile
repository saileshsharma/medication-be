FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Download NLTK data as root, then fix permissions
RUN python -c "import nltk; nltk.download('punkt', quiet=True)" 2>/dev/null || echo "NLTK punkt not downloaded, will download on first use" \
    && python -c "import nltk; nltk.download('punkt_tab', quiet=True)" 2>/dev/null || true

# Create non-root user and set permissions
RUN useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app \
    && mkdir -p /home/appuser/nltk_data \
    && chown -R appuser:appuser /home/appuser/nltk_data

# Switch to non-root user
USER appuser

# Set NLTK data path
ENV NLTK_DATA=/home/appuser/nltk_data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run the application with production settings
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--log-level", "info"]

# Use official lightweight Python 3.12 image
FROM python:3.12-slim

# Set environment variables to optimize Python for containerized execution
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SECRET_KEY=dev_secret_key_revision_shield_2026_super_secure \
    PORT=8000

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (curl for healthchecks if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Expose FastAPI application port
EXPOSE 8000

# Start FastAPI application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

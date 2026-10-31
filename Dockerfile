FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project source files into the image context
COPY . .

# Install the package in editable or standard mode so 'mantagu' package namespaces resolve
RUN pip install --no-cache-dir -e .

# Expose internal port
EXPOSE 8080

# Run Uvicorn directly, routing host and port dynamically via environment variables
CMD ["uvicorn", "src.mantagu.api:app", "--host", "0.0.0.0", "--port", "8080"]

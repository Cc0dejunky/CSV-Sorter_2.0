FROM python:3.10-slim

# Synchronized with docker-compose volume
WORKDIR /app

# Install CPU-only torch to save space
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .
# Use official Python image
FROM python:3.11-slim

# Install system dependencies for OpenCV + Mediapipe
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the port (Railway injects PORT env)
EXPOSE 8000

# Run Uvicorn, expanding PORT from env
CMD uvicorn exercise_api_backend:app --host 0.0.0.0 --port ${PORT}
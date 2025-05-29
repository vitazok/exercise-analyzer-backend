# Use official Python image
FROM python:3.11-slim

# Install system dependencies + build tools
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Install latest pip, setuptools, wheel
RUN pip install --upgrade pip setuptools wheel

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose port
EXPOSE 8000

# Default run command
CMD ["python", "-m", "uvicorn", "exercise_api_backend:app", "--host", "0.0.0.0", "--port", "8000"]

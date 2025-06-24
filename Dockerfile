# Use official Python image
FROM python:3.10-slim

# Prevent .pyc files and enable real-time logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory in container
WORKDIR /app

# Install system packages required for pyodbc
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gnupg \
    curl \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .

# Expose port Flask will listen on
EXPOSE 8000

# Run the app
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]

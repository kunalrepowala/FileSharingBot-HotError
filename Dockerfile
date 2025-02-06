FROM python:3.12-slim

# Install system dependencies for building aiohttp, ffmpeg, and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libpq-dev \
    ffmpeg \
    libjpeg-turbo8-dev \      # Add libjpeg-turbo
    libpng-dev \              # Add libpng
    clang \                   # Install clang (as mentioned in your requirements.txt)
    && rm -rf /var/lib/apt/lists/*

# Check if ffmpeg was installed successfully (optional debugging step)
RUN ffmpeg -version

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app into the container
COPY . .

# Ensure ffmpeg is available to ffmpeg-python
ENV FFMPEG_BINARY=/usr/bin/ffmpeg

# Command to run the application
CMD ["python", "main.py"]

FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    chromium \
    chromium-driver \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install yt-dlp with browser cookie support
RUN pip install --upgrade pip && \
    pip install "yt-dlp[web]" flask

# Set environment variables to use Chromium in headless mode
ENV BROWSER=chromium

# Copy your app code
WORKDIR /app
COPY . .

# Run Flask app
CMD ["python", "server.py"]


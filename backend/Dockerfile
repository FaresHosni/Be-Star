FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    fonts-noto-color-emoji \
    fonts-dejavu \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Arabic Fonts (Amiri)
RUN mkdir -p /app/fonts && \
    curl -L https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf -o /app/fonts/Amiri-Regular.ttf && \
    curl -L https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Bold.ttf -o /app/fonts/Amiri-Bold.ttf

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory if it doesn't exist
RUN mkdir -p data

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

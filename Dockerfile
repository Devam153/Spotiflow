# Use a lightweight Python base image
FROM python:3.9-slim-bullseye
# Install system dependencies (including tesseract)
RUN apt-get update && \
    apt-get install -y tesseract-ocr && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port (default for Render)
EXPOSE 8000

# Start Gunicorn server
CMD ["gunicorn", "spotiflow.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "120"]

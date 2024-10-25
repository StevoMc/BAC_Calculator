# Build stage
FROM python:3.10-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt ./ 
RUN pip install --no-cache-dir -r requirements.txt && \
  ls /usr/local/lib/python3.10/site-packages

# Runtime stage
FROM python:3.10-slim

RUN apt-get update && apt-get install -y curl

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  FLASK_ENV=production

# Create a non-root user
RUN adduser --disabled-password appuser

# Set the working directory
WORKDIR /app

# Create the flask_session directory and set permissions
RUN mkdir -p /tmp/flask_session && chown -R appuser:appuser /tmp/flask_session
RUN mkdir -p /app/flask_session && chown -R appuser:appuser /app/flask_session

# Copy dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code
COPY . .

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl --fail http://localhost:5000/health-check || exit 1

# Use Gunicorn to serve the app with gevent worker
CMD ["gunicorn", "-w", "4", "-k", "gevent", "-b", "0.0.0.0:5000", "main:app"]

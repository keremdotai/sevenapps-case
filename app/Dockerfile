# Official Python image
FROM python:3.11-slim

# Working directory
WORKDIR /app

# Build arguments
ARG PORT

# Install appitudes
RUN apt-get update && \
        apt-get install -y gcc && \
        rm -rf /var/lib/apt/lists/*

# Install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source directory
COPY ./src ./src

# Port
EXPOSE ${PORT}

# Run the application
CMD gunicorn src.main:app --bind 0.0.0.0:${PORT} --preload \
        --workers ${NUM_WORKERS} --worker-class=uvicorn.workers.UvicornWorker \
        --capture-output --access-logfile '-' --error-logfile '-' \
        --timeout 0

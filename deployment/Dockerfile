
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set working directory
WORKDIR /app

# Install Python and dependencies
RUN apt-get update && \
    apt-get install -y python3-pip python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ /app/
COPY monitoring/ /app/monitoring/
COPY security/ /app/security/

# Add model serving script
COPY serve.py .

# Create model directory
RUN mkdir -p /models

# Environment variables
ENV MODEL_PATH=/models/bloom-finetuned-sentiment
ENV CUDA_VISIBLE_DEVICES=0
ENV SERVING_PORT=8000
ENV LOG_LEVEL=INFO
ENV MAX_BATCH_SIZE=32
ENV ENABLE_SECURITY=true
ENV ENABLE_MONITORING=true

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8000/health || exit 1

# Run the server
CMD ["python3", "serve.py"]

FROM python:3.11-slim

WORKDIR /app

# Combine RUN commands to reduce layers and optimize for EC2
# RUN apt-get update && apt-get install -y \
#     gcc \
#     postgresql-client \
#     python3-dev \
#     libpq-dev \
#     build-essential \
#     curl \
#     && apt-get clean \
#     && apt-get autoremove -y \
#     && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
#     && pip install --no-cache-dir --upgrade pip

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agents/ ./agents/
COPY api/ ./api/
COPY chains/ ./chains/
COPY chat_history/ ./chat_history/
COPY config/ ./config/
COPY models/ ./models/
COPY rag/ ./rag/
COPY utils/ ./utils/

# Reduce logging verbosity for production
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Use production settings for uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"] 
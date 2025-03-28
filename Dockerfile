FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and build tools
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    python3-dev \
    libpq-dev \
    build-essential \
    curl \
    && apt-get clean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy only necessary project files
COPY agents/ ./agents/
COPY api/ ./api/
COPY chains/ ./chains/
COPY chat_history/ ./chat_history/
COPY config/ ./config/
COPY models/ ./models/
COPY rag/ ./rag/
COPY utils/ ./utils/
COPY requirements.txt .

# Upgrade pip and install requirements in one layer
RUN pip install --no-cache-dir --upgrade pip 
RUN pip install --no-cache-dir -r requirements.txt

# Print directory structure for debugging
RUN echo "Project structure:" && \
    ls -la && \
    echo "\nVerifying key directories:" && \
    for dir in agents api chains chat_history cli config data graphs models rag tests utils; do \
        echo "\n$dir directory:" && \
        ls -la $dir/; \
    done

# Expose the port the app runs on
EXPOSE 8000

# Add environment variables if needed
ENV PYTHONPATH=/app

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Command to run the application with more verbose output
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"] 
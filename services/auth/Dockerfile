# services/auth-api/Dockerfile
FROM python:3.12-slim

# Ensure output is shown immediately and no pycache
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose FastAPI port
EXPOSE 8002

# Start the auth service
CMD ["uvicorn", "auth.main:app", "--host", "0.0.0.0", "--port", "8002"]

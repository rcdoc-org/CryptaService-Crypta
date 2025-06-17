# services/auth/Dockerfile
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Patch flask-mongoengine/json.py in-place so it falls back to DefaultJSONProvider
RUN sed -i \
    -e '1i\try:\n    from flask.json import JSONEncoder\nexcept ImportError:\n    from flask.json.provider import DefaultJSONProvider as JSONEncoder\n' \
    /usr/local/lib/python3.12/site-packages/flask_mongoengine/json.py

COPY . .
EXPOSE 8002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]

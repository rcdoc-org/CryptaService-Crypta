FROM python:3.12-slim-bullseye

RUN apt-get update && \
    apt-get install -y pkg-config default-libmysqlclient-dev build-essential && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip

WORKDIR /app

COPY ./requirements.txt /app

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 3000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:3000"]
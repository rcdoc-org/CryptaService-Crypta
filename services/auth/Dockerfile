FROM python:3.12-slim-bullseye

# Install required system packages, ODBC driver, and build tools
RUN apt-get update && \
    apt-get install -y curl gnupg apt-transport-https && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y \
        msodbcsql17 \
        unixodbc \
        unixodbc-dev \
        gcc \
        g++ \
        libpq-dev \
        libssl-dev \
        libffi-dev \
        python3-dev \
        libsasl2-dev \
        libodbc1 \
        odbcinst \
        pkg-config \
        default-libmysqlclient-dev \
        build-essential && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app source code
COPY . /app

# Expose Django development server port
EXPOSE 8002

# Default command
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8002"]

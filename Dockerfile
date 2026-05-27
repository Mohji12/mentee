FROM public.ecr.aws/lambda/python:3.11

# Set working directory
WORKDIR /var/task

# Copy requirements first (better caching)
COPY requirements.txt .

# Install minimal system dependencies
RUN yum install -y \
        libpng \
        libjpeg-turbo \
        freetype \
        freetype-devel \
        libpng-devel \
        zlib-devel \
        chromium \
        atk \
        at-spi2-atk \
        gtk3 \
        libXcomposite \
        libXcursor \
        libXdamage \
        libXext \
        libXi \
        libXrandr \
        libXScrnSaver \
        libXtst \
        cups-libs \
        libXss \
        libasound2 \
    && yum clean all

# Upgrade pip and install Python packages
RUN pip install --upgrade pip setuptools wheel

# Install Python packages with verbose output and error handling
RUN pip install --no-cache-dir -r requirements.txt -t . -v || \
    (echo "ERROR: Package installation failed. Checking requirements.txt..." && \
     cat requirements.txt && \
     exit 1)

# Verify critical packages are installed
RUN python -c "import fastapi; import sqlalchemy; import pymysql; import bcrypt; import pydantic; print('✓ Core packages verified')" || \
    (echo "ERROR: Package verification failed!" && \
     ls -la /var/task/ | head -20 && \
     exit 1)

# Copy application code
COPY app/ ./app

# Lambda entrypoint
CMD ["app.main.handler"]

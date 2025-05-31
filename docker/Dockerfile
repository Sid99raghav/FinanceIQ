# Use a smaller base image
ARG registry=library
ARG base=ubuntu
ARG version=22.04
FROM $registry/$base:$version

# Set environment variables to avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        wget \
        python3-pip \
        curl \
        sendmail \
        less \
        bc \
        vim \
        libsasl2-dev \
        python3-dev \
        libldap2-dev \
        libssl-dev \
        libsqlite3-dev \
        sqlite3 \
        net-tools \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
ADD requirements.txt /home/
# Install additional Python dependencies
RUN pip install \
        sqlalchemy \
        jinja2==3.0.3 \
        pyopenssl \
        python-multipart \
        pyyaml \
        telepot \
        colorlog \
        ruff \
        fastapi-sso \
        python-jose[cryptography] \
        pydantic \
        passlib[bcrypt] \
        authlib \
        fastapi-mail \
        requests \
        uvicorn \
        google-generativeai \
        openai \
        itsdangerous \
        fuzzywuzzy \
        python-Levenshtein \
        PyPDF2

# Copy application code to the container
COPY . /home

# Set working directory
WORKDIR /home
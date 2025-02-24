
FROM python:3.12.0-slim

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Setup env variable
ENV DOCKER_HOME=/home/app/web

# Set work directory
RUN mkdir -p ${DOCKER_HOME}
WORKDIR ${DOCKER_HOME}

# Python env variables
ENV PYTHONDONOTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install basic dependencies and Python
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3-pip \
    software-properties-common \
    gnupg \
    curl \
    nmap \
    gcc \
    python3-dev \
    libpq-dev \
    libopencv-dev \
    python3-opencv \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Add Mosquitto repository and install
RUN apt-add-repository ppa:mosquitto-dev/mosquitto-ppa && \
    apt-get update && \
    apt-get install -y mosquitto mosquitto-clients && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt ${DOCKER_HOME}/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . ${DOCKER_HOME}/

# Expose ports for FastAPI and MQTT
EXPOSE 8000 1883

# Start Mosquitto service and FastAPI app
CMD service mosquitto start && fastapi run app.py --host 0.0.0.0

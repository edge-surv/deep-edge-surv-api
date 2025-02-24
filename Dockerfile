# Use the Python slim base image
FROM python:3.12.0-slim

# Set up environment variables
ENV DOCKER_HOME=/home/app/web

# Set the working directory
RUN mkdir -p ${DOCKER_HOME}
WORKDIR ${DOCKER_HOME}

# Python environment variables
ENV PYTHONDONOTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade pip
RUN pip install --upgrade pip

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nmap \
    libgl1 \
    gcc \
    python3-dev \
    libpq-dev \
    libopencv-dev \
    python3-opencv \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    mosquitto \
    mosquitto-clients && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt ${DOCKER_HOME}/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . ${DOCKER_HOME}/

# Expose ports for FastAPI and Mosquitto
EXPOSE 8000 1883

# Start Mosquitto and run the FastAPI app
CMD fastapi run app.py --host 0.0.0.0 --port 8000
# Use the Python slim base image
FROM python:3.12.0-slim

# Set up environment variables
ENV DOCKER_HOME=/home/app/web

# Set the working directory
RUN mkdir -p ${DOCKER_HOME}
WORKDIR ${DOCKER_HOME}

# Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install git
RUN apt install git

# Upgrade pip
RUN pip install --upgrade pip

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    gcc \
    python3-dev \
    libpq-dev \
    libopencv-dev \
    python3-opencv \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt ${DOCKER_HOME}/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir ultralytics supervision "fastapi[standard]" 
RUN pip install --no-cache-dir git+https://github.com/openai/CLIP.git

# Copy the rest of the application code
COPY . ${DOCKER_HOME}/

# Expose port for FastAPI
EXPOSE 9000

# Start the FastAPI app
CMD ["fastapi", "run", "app.py", "--host", "0.0.0.0", "--port", "9000"]

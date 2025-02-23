# the python base image
FROM python:3.12.0-slim

# setup env variable
ENV DOCKER_HOME=/home/app/web

# set work directory
RUN mkdir -p ${DOCKER_HOME}
WORKDIR ${DOCKER_HOME}

# python env variables
ENV PYTHONDONOTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# upgrade pip
RUN pip install --upgrade pip

# install nmap and avahi-daemon
RUN apt-get update && apt-get install -y nmap && rm -rf /var/lib/apt/lists/*

# install gcc, python3-dev, and OpenCV dependencies
RUN apt-get update && apt-get install -y libgl1 \
    gcc \
    python3-dev \
    libpq-dev \
    libopencv-dev \
    python3-opencv \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6

# copy requirements.txt first to leverage Docker cache
COPY requirements.txt ${DOCKER_HOME}/

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest of the application code
COPY . ${DOCKER_HOME}/

# expose port for fastapi app
EXPOSE 8000

CMD ["fastapi", "run", "app.py", "--host", "0.0.0.0"]

# Use a mirror for the base image to ensure accessibility in China
FROM docker.m.daocloud.io/python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Change apt sources to Aliyun mirror for speed and accessibility in China
# Handle both sources.list and debian.sources (Debian 12+)
RUN if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources; \
    else \
        sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list; \
    fi && \
    # Also replace security sources if possible, though strict security might want original. 
    # For dev/MVP, using mirror is safer for success.
    if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources; \
    fi

# Install system dependencies
# Added openssh-client to support git clone via SSH
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install Python dependencies using Tsinghua mirror
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

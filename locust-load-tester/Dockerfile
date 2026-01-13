# Use an official Python runtime as a parent image
FROM python:3.9.18-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Install build tools and libev-dev required for gevent
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libev-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Locust and any other necessary dependencies
# We install eventlet==0.33.3 to avoid a dependency conflict
# and set the desired version for locust
RUN pip install --no-cache-dir locust==2.20.1 eventlet==0.33.3

# Copy the locustfile into the container
COPY . /app

# Expose the web UI port
EXPOSE 8089

# Command to run Locust
CMD ["locust", "-f", "locustfile.py"]

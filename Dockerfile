FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install system dependencies
RUN apt-get update && apt-get install -y \
    iverilog \
    python3 \
    python3-pip \
    python3-numpy \
    python3-matplotlib \
    make \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY tools/requirements-minimal.txt /tmp/
RUN pip3 install -r /tmp/requirements-minimal.txt

# Set working directory
WORKDIR /workspace

# Default command
CMD ["/bin/bash"]

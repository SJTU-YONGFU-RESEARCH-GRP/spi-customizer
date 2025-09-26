FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    iverilog \
    gtkwave \
    python3 \
    python3-pip \
    make \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY tools/requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

# Set working directory
WORKDIR /workspace

# Default command
CMD ["/bin/bash"]

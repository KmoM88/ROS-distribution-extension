FROM ubuntu:noble

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install core dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    sudo \
    ruby \
    && rm -rf /var/lib/apt/lists/*

# Set up the workspace directory
WORKDIR /workspace

# Copy the local workspace files into the container
COPY . /workspace

# Remove broken .git files from submodules to allow git commands (e.g. ls-remote) inside the container
RUN find submodules/ -name .git -type f -delete

ENV ROSDEP_LOCAL_DEV=true

# Create and activate python virtual environment, then install submodules
RUN python3 -m venv .venv \
    && .venv/bin/pip install --upgrade pip \
    && .venv/bin/pip install \
        -e submodules/kmom88-rosdistro[test] \
        -e submodules/kmom88-rosdep[test] \
        -e submodules/kmom88-rosinstall_generator \
        -e submodules/kmom88-ros_buildfarm[test] \
        -e submodules/kmom88-bloom[test] \
        -e submodules/kmom88-superflore

# Initialize rosdep system-wide inside the container
RUN .venv/bin/rosdep init || true

# Run update as root (in Docker) to pull public rosdep sources
RUN .venv/bin/rosdep update || true

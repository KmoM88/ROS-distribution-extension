# Workflow 1: Repository Setup & Environment Management

This document details the setup procedure, configuration files, and validation steps executed for **Workflow 1: Repository Setup & Environment Management**.

---

## 1. Overview
* **Agent**: Environment Manager Agent
* **Role**: Responsible for workspace setup, submodule layout, fork alignment, virtual environment provisioning, and mock environment creation.
* **Goal**: Establish a clean, isolated environment to perform safe testing and implementation of REP-2015 without altering the global host system.

---

## 2. Workspace & Git Submodule Layout
The development forks of the critical tools were successfully added and initialized as submodules in the main workspace repository:

| Submodule / Fork Repository | Local Path |
| :--- | :--- |
| `reps` | `submodules/reps` |
| `rosdistro` | `submodules/kmom88-rosdistro` |
| `rosdep` | `submodules/kmom88-rosdep` |
| `rosinstall_generator` | `submodules/kmom88-rosinstall_generator` |
| `ros_buildfarm` | `submodules/kmom88-ros_buildfarm` |

### Verification of Submodule Commits
To check the current Checked-out status and commits:
```bash
git submodule status
```

---

## 3. Python Virtual Environment in Docker
To maintain complete environment isolation and prevent package contamination on the host system, a Python virtual environment is configured inside a Docker container (based on `ubuntu:noble` to match REP-2000 specifications).

### Setup Instructions
1. **Dockerfile Configuration**:
   The `docker/Dockerfile` sets up the container and creates the internal virtual environment:
   ```dockerfile
   FROM ubuntu:noble
   RUN apt-get update && apt-get install -y python3 python3-pip python3-venv git curl sudo
   WORKDIR /workspace
   COPY . /workspace
   RUN python3 -m venv .venv \
       && .venv/bin/pip install --upgrade pip \
       && .venv/bin/pip install -e submodules/kmom88-rosdistro \
       && .venv/bin/pip install -e submodules/kmom88-rosdep \
       && .venv/bin/pip install -e submodules/kmom88-rosinstall_generator \
       && .venv/bin/pip install -e submodules/kmom88-ros_buildfarm
   ```

2. **Run Tests Script**:
   The helper script `docker/run_tests.sh` automates the build and run phases:
   ```bash
   #!/bin/bash
   docker build -t ros-distro-ext-test -f docker/Dockerfile .
   docker run --rm ros-distro-ext-test bash -c "..."
   ```

### Check Installed Packages in Docker
During the build or container run, you can list the installed packages to verify the correct editable links:
```bash
docker run --rm ros-distro-ext-test .venv/bin/pip list
```

---

## 4. Baseline Mock Environment
A testing baseline is established inside `tests/workflow_1/` to represent standard REP-143 index (version 3) and REP-143 distribution (version 2) formats.

### Index File: `tests/workflow_1/index.yaml`
```yaml
%YAML 1.1
---
distributions:
  rolling:
    distribution:
      - rolling/distribution.yaml
type: index
version: 3
```

### Distribution File: `tests/workflow_1/rolling/distribution.yaml`
```yaml
%YAML 1.1
---
release_platforms:
  ubuntu: [noble]
  debian: [bookworm]
repositories:
  ros_tutorials:
    doc:
      type: git
      url: https://github.com/ros/ros_tutorials.git
      version: rolling-devel
    release:
      packages:
        - turtlesim
      tags:
        release: release/{package}/{version}
      url: https://github.com/ros-gbp/ros_tutorials-release.git
      version: 0.3.9
    source:
      type: git
      url: https://github.com/ros/ros_tutorials.git
      version: rolling-devel
    status: maintained
tags:
  - rolling
type: distribution
version: 2
```

---

## 5. Verification Commands
To verify the environment is correctly parsing the baseline configuration inside the Docker container:

```bash
docker run --rm ros-distro-ext-test .venv/bin/python3 -c "import rosdistro; idx = rosdistro.get_index('file:///workspace/tests/workflow_1/index.yaml'); dist = rosdistro.get_distribution_file(idx, 'rolling'); print(dist.repositories.keys())"
```

### Expected Output
```json
dict_keys(['ros_tutorials'])
```
*Status: Verified and working inside the container.*

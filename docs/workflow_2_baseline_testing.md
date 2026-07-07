# Workflow 2: Testing Current Behavior (Baseline)

This document details the setup, configuration files, and verification steps executed for **Workflow 2: Testing Current Behavior (Baseline)** using isolated test directories and a Docker container.

---

## 1. Overview
* **Agent**: Baseline QA Agent
* **Role**: Responsible for testing unmodified tools against REP-141/143 overlays and REP-2000 target platforms in a safe, reproducible environment.
* **Goal**: Validate overlay merging logic, build cache compilation, and ensure `rosinstall_generator` and `rosdep` can retrieve baseline distribution data successfully without interfering with the host system files.

---

## 2. Segregated Test Configuration
To ensure each workflow remains independent and reproducible, tests for Workflow 2 are located under the `tests/workflow_2/` directory:

* **Index File**: [tests/workflow_2/index.yaml](../tests/workflow_2/index.yaml) (references both the base and overlay files).
* **Base Distribution File**: [tests/workflow_2/rolling/distribution.yaml](../tests/workflow_2/rolling/distribution.yaml) (defines standard `ros_tutorials` repository with `turtlesim` at version `0.3.9`).
* **Overlay File**: [tests/workflow_2/rolling/overlay.yaml](../tests/workflow_2/rolling/overlay.yaml) (overrides `ros_tutorials` status to `developed` and adds the `new_repo` entry).

---

## 3. Docker Testing Environment
To prevent polluting the host system (such as writing to `/etc/ros/rosdep`), all system-level and integration tests are run inside an isolated Docker container based on `ubuntu:noble` (supporting Python 3.12).

### Docker Configuration
* **Dockerfile**: [docker/Dockerfile](../docker/Dockerfile)
  * Sets up the `ubuntu:noble` base.
  * Installs package manager dependencies.
  * Copies the workspace and installs the 4 tool submodules in editable mode.
  * Runs `rosdep init` and `rosdep update` inside the container.
* **Execution Script**: [docker/run_tests.sh](../docker/run_tests.sh)
  * Builds the Docker image: `ros-distro-ext-test`.
  * Runs the test suite in the container.

---

## 4. Test Verification Script
The Python script [tests/workflow_2/test_workflow_2.py](../tests/workflow_2/test_workflow_2.py) validates the overlay merging behavior:

* Verifies `rosdistro.get_distribution_file` merges the base file and `overlay.yaml` cleanly.
* Asserts that `ros_tutorials` has status `developed` (overridden from `maintained`).
* Asserts that the new repository `new_repo` is present in the merged list.
* Asserts that the base package `turtlesim` remains intact in the merged specification.

---

## 5. Verification Commands Run inside Container
1. **Python Overlay Parsing Test**:
   ```bash
   .venv/bin/python3 tests/workflow_2/test_workflow_2.py
   ```
2. **Build Distribution Cache**:
   ```bash
   .venv/bin/rosdistro_build_cache file:///workspace/tests/workflow_2/index.yaml rolling
   ```
   *Generates `rolling-cache.yaml` and `rolling-cache.yaml.gz` relative to `index.yaml` under `tests/workflow_2/`.*
3. **Run rosinstall_generator**:
   ```bash
   ROSDISTRO_INDEX_URL=file:///workspace/tests/workflow_2/index.yaml .venv/bin/rosinstall_generator turtlesim --rosdistro rolling --tar
   ```
4. **Run rosdep Database Check**:
   ```bash
   ROSDISTRO_INDEX_URL=file:///workspace/tests/workflow_2/index.yaml .venv/bin/rosdep db
   ```

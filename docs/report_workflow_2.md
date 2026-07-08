# Workflow 2 Status Report: Testing Current Behavior (Baseline)

This report details the execution, configurations, and results of **Workflow 2: Testing Current Behavior (Baseline)**.

---

## 1. Objectives & Setup Criteria
The purpose of Workflow 2 was to verify that the unmodified ROS toolchain correctly handles the standard REP-143 overlay and merge behaviors (without extends) and that the baseline packages can compile build caches and resolve dependencies inside the isolated Docker environment.

---

## 2. Segregated Test Configurations
A dedicated directory `tests/workflow_2/` was structured to represent an overlay layout:
- **Base Distribution**: [tests/workflow_2/rolling/distribution.yaml](../tests/workflow_2/rolling/distribution.yaml) (declares `ros_tutorials` repository with `turtlesim` at version `0.3.9` and status `maintained`).
- **Overlay File**: [tests/workflow_2/rolling/overlay.yaml](../tests/workflow_2/rolling/overlay.yaml) (overrides `ros_tutorials` status to `developed` and introduces a new repository `new_repo`).
- **Overlay Index**: [tests/workflow_2/index.yaml](../tests/workflow_2/index.yaml) (combines both files).

---

## 3. Local Verification Results
The test script [tests/workflow_2/test_workflow_2.py](../tests/workflow_2/test_workflow_2.py) was executed inside the container:
```bash
.venv/bin/python3 tests/workflow_2/test_workflow_2.py
```
**Results & Assertions**:
- `rosdistro` successfully parsed the overlay configuration.
- Asserted that `ros_tutorials` repository was overridden to status `developed`.
- Asserted that `new_repo` was successfully merged into the list of repositories.
- Asserted that the base package `turtlesim` remained intact.

---

## 4. Downstream Tool Baseline Dry-Runs
To confirm that unmodified tools operate correctly with the merged configurations, the following commands were validated inside the Docker container:

1. **rosdistro_build_cache**:
   ```bash
   .venv/bin/rosdistro_build_cache file:///workspace/tests/workflow_2/index.yaml rolling
   ```
   - *Result*: Successfully compiled and output `rolling-cache.yaml` and `rolling-cache.yaml.gz` under `tests/workflow_2/`.
2. **rosinstall_generator**:
   ```bash
   ROSDISTRO_INDEX_URL=file:///workspace/tests/workflow_2/index.yaml .venv/bin/rosinstall_generator turtlesim --rosdistro rolling --tar
   ```
   - *Result*: Successfully generated standard `.rosinstall` tarball configuration for the merged package.
3. **rosdep**:
   ```bash
   ROSDISTRO_INDEX_URL=file:///workspace/tests/workflow_2/index.yaml .venv/bin/rosdep db
   ```
   - *Result*: Successfully compiled the local database containing package configurations from both the base and overlay files.

# Workflow 9 Status Report: Lyrical and Gazebo Jetty Integration

This report details the execution, configurations, and verification results of **Workflow 9: Lyrical and Gazebo Jetty Integration**.

---

## 1. Objectives & Setup Criteria

The main objective of Workflow 9 is to establish a real-world integration where **`lyrical`** acts as a downstream ROS 2 distribution extending the custom **`jetty`** Gazebo distribution:

1. **Submodule Integration**:
   - Upstream Gazebo distribution: `submodules/gazebodistro` (branch `jrivero/jetty-rosdistro`).
   - Downstream ROS distribution: `submodules/ros-rosdistro` (user fork containing `lyrical/distribution.yaml`).
2. **Direct Downstream Extension**:
   - `submodules/ros-rosdistro/lyrical/distribution.yaml` directly extends `jetty` via `source_rebuild` without needing an intermediate overlay distribution.
3. **Repository Specification Merging**:
   - Merging parent repository attributes (`source`, `doc`, `release`) into the child repository so downstream distributions can specify release versions while inheriting the parent's upstream source Git repository configuration.
4. **Toolchain Verification**:
   - **`rosdistro`**: Verification of in-memory chained resolution across distributions using the real `lyrical` distribution file and in-memory chained cache resolution.
   - **`rosinstall_generator`**: Verification of workspace checkout definitions generated for inherited Gazebo packages (`gz-sim`).
   - **`rosdep`**: Verification of package name and distro prefix resolution for downstream packages across both standard ROS packages (`ros-lyrical-std-msgs`, `ros-lyrical-turtlesim`) and Gazebo integration packages (`ros-lyrical-ros-gz-sim`, `ros-lyrical-ros-gz-bridge`).
5. **Selective Test Runner**:
   - Configured `docker/run_tests.sh` to accept target arguments (e.g. `docker/run_tests.sh 9`) for fast targeted testing.

---

## 2. Configuration & Implementation Details

### A. Index Configuration (`tests/workflow_9/index.yaml`)
```yaml
distributions:
  jetty:
    distribution: [../../submodules/gazebodistro/rosdistro/jetty/distribution.yaml]
    distribution_cache: ../../submodules/gazebodistro/rosdistro/jetty-cache.yaml
    distribution_type: ros2
    python_version: 3
  lyrical:
    distribution: [../../submodules/ros-rosdistro/lyrical/distribution.yaml]
    distribution_cache: lyrical-cache.yaml
    distribution_type: ros2
    python_version: 3
type: index
version: 4
```

### B. Downstream Distribution File (`submodules/ros-rosdistro/lyrical/distribution.yaml`)
Upgraded header to format version 3 with `extends` block targeting `jetty`:
```yaml
%YAML 1.1
# ROS distribution file
# see REP 143: http://ros.org/reps/rep-0143.html
---
type: distribution
version: 3
extends:
  - distro_name: jetty
    extension_method: source_rebuild
release_platforms:
  debian:
  - trixie
  fedora:
  - '43'
  rhel:
  - '10'
  ubuntu:
  - resolute
repositories:
  ...
```

---

## 3. Verification Results

Running the isolated test with the targeted runner:
```bash
docker/run_tests.sh 9
```

Output:
```bash
==========================================================
Running tests ('9') inside isolated Docker container...
==========================================================
Running Workflow 9 Lyrical & Gazebo Jetty Rebuild Test...
WARNING: Target platform 'debian:trixie' specified in derived distribution is not supported by base distribution.
WARNING: Target platform 'fedora:43' specified in derived distribution is not supported by base distribution.
WARNING: Target platform 'rhel:10' specified in derived distribution is not supported by base distribution.
WARNING: Target platform 'ubuntu:resolute' specified in derived distribution is not supported by base distribution.
WARNING: Target platform 'debian:trixie' specified in derived distribution is not supported by base distribution.
WARNING: Target platform 'fedora:43' specified in derived distribution is not supported by base distribution.
WARNING: Target platform 'rhel:10' specified in derived distribution is not supported by base distribution.
WARNING: Target platform 'ubuntu:resolute' specified in derived distribution is not supported by base distribution.
############################################################
Loading Workflow 9 index from: file:///workspace/tests/workflow_9/index.yaml
############################################################
Loading distribution file for 'lyrical' from submodule...
Inherited Gazebo source repository 'gz-sim' verified successfully.
Loading cached distribution for 'lyrical' (testing chained in-memory cache)...
In-memory chained cache packages verified successfully.
Testing rosinstall_generator repository resolution for inherited Gazebo package...
Rosinstall generator output:
- git:
    local-name: gz-sim
    uri: https://github.com/gazebosim/gz-sim
    version: 10.5.0


Testing rosdep package resolutions under source_rebuild...
Query rosdistro index file:///workspace/tests/workflow_9/index.yaml
Add distro "jetty"
Add distro "lyrical"
lyrical turtlesim resolves to: ['ros-lyrical-turtlesim']
lyrical std_msgs resolves to: ['ros-lyrical-std-msgs']
lyrical ros_gz_sim resolves to: ['ros-lyrical-ros-gz-sim']
lyrical ros_gz_bridge resolves to: ['ros-lyrical-ros-gz-bridge']
rosdep package resolutions for all targeted packages verified successfully.
Workflow 9 verification test PASSED!
All selected tests for '9' PASSED successfully!
```

# Workflow 4: Testing Extension Methods & Toolchain Integration

This document details the design, implementation, and verification steps executed for **Workflow 4: Testing Extension Methods & Toolchain Integration** in an isolated environment.

---

## 1. Overview
* **Agent**: Toolchain Integrator Agent
* **Role**: Responsible for updating client tools to support `binary_import` and `source_rebuild` runtime behaviors, package renaming, and aliasing.
* **Goal**: Validate that `rosdep` and `rosinstall_generator` query packages correctly across distribution boundaries, mapping package names to the correct binary name depending on the extension method.

---

## 2. Git Branching
To ensure modifications to tool forks are tracked properly, the following feature branches were checked out:
* **rosdep Submodule**: `submodules/kmom88-rosdep` -> Branch: `feature/rep-2015-tool-integration`
* **rosinstall_generator Submodule**: `submodules/kmom88-rosinstall_generator` -> Branch: `feature/rep-2015-tool-integration`
* **ros_buildfarm Submodule**: `submodules/kmom88-ros_buildfarm` -> Branch: `feature/rep-2015-tool-integration`
* **bloom Submodule**: `submodules/kmom88-bloom` -> Branch: `feature/rep-2015-tool-integration`
* **superflore Submodule**: `submodules/kmom88-superflore` -> Branch: `feature/rep-2015-tool-integration`

---

---

## 3. Architecture Requirement: Generic Binary Package Name Transformation in `rosdistro`

Under REP-2015, distribution extensions require dynamic binary packaging rules (`binary_import`, `source_rebuild`, non-ROS ecosystems like Gazebo, custom prefix templates, and explicit package overrides).

To prevent fragmented and conflicting naming logic across client tools (`rosdep`, `ros_buildfarm`, `bloom`, `superflore`), **`rosdistro` is established as the single source of truth** for computing OS binary package names using an ecosystem-agnostic transformation model:

### 3.1. Requirements & Transformation Model
1. **Generic Prefix Template (`binary_prefix`)**:
   - Standard ROS distributions default to `"ros-{DISTRO}-"` with standard package underscore-to-dash normalization (e.g., `std_msgs` $\rightarrow$ `ros-rolling-std-msgs`).
   - Standalone distributions (e.g. Gazebo `jetty`) or `extends` declarations specify `binary_prefix: ""` to disable prefixes and preserve native package names (e.g. `gz-sim10`, `gz-cmake5`).
2. **Sequential Regular Expression Rules (`binary_name_rules`)**:
   - Supports a list of regex search-and-replace rules executed in sequence:
     ```yaml
     binary_name_rules:
       - search: "_"
         replace: "-"
       - search: "^(.*)$"
         replace: "ros-{DISTRO}-\\1"
     ```
3. **Template Variable Interpolation**:
   - `{DISTRO}` / `{distro}`: Target distribution name (normalized).
   - `{PACKAGE}` / `{package}`: Source package name (normalized).
   - `{ORIGIN_DISTRO}` / `{origin_distro}`: Origin parent distribution name (for `binary_import`).
4. **Reverse Binary Alias Resolution**:
   - Provides `get_package_name_from_binary(binary_name)` on `DistributionFile` via deterministic in-memory lookup table and prefix-stripping fallback.
5. **`binary_import` Resolution**:
   - Inherits and evaluates the parent distribution's binary naming rules: `ros-{origin_distro}-{pkg_name}`.
6. **`source_rebuild` Resolution**:
   - Rebuilt packages target the child distribution's prefix or rules: `ros-{derived_distro}-{pkg_name}`.

---

## 4. Code Modifications & Toolchain Delegation

### 4.1. `rosdistro` (Source of Truth Engine)
* **`ReleaseRepositorySpecification`** ([release_repository_specification.py](https://github.com/KmoM88/rosdistro/blob/feature/rep-2015-v3-parser/src/rosdistro/release_repository_specification.py)): Implemented `get_binary_package_name(pkg_name)` evaluating explicit overrides, sequential `binary_name_rules`, prefix templates (`binary_prefix`), and variable substitutions.
* **`DistributionFile`** ([distribution_file.py](https://github.com/KmoM88/rosdistro/blob/feature/rep-2015-v3-parser/src/rosdistro/distribution_file.py)): Added `get_binary_package_name(pkg_name)`, `get_package_name_from_binary(binary_name)`, and updated `merge_extends()` to propagate `binary_prefix` and `binary_name_rules` down parent chains.

### 4.2. `rosdep` Delegation
* In [gbpdistro_support.py](https://github.com/KmoM88/rosdep/blob/feature/rep-2015-tool-integration/src/rosdep2/gbpdistro_support.py): Replaced hardcoded string formatting by calling `repo.release_repository.get_binary_package_name(pkg)` directly from `rosdistro` (with graceful fallback for older `rosdistro` versions).

### 4.3. `ros_buildfarm` Delegation
* In [common.py](https://github.com/KmoM88/ros_buildfarm/blob/feature/rep-2015-tool-integration/ros_buildfarm/common.py): Updated `get_os_package_name(rosdistro_name, package_name, dist_file)` to delegate directly to `dist_file.get_binary_package_name(package_name)`.

### 4.4. `superflore` ebuild categories
In [ebuild.py](https://github.com/KmoM88/superflore/blob/feature/rep-2015-tool-integration/superflore/generators/ebuild/ebuild.py) and [gen_packages.py](https://github.com/KmoM88/superflore/blob/feature/rep-2015-tool-integration/superflore/generators/ebuild/gen_packages.py):
* Transitioned internal ebuild dependency tracker lists to dicts.
* Resolved `origin_distro` from the `rosdistro` repository structure dynamically and passed it to the ebuild generator.
* Generated correct Gentoo Portage categories as `ros-${dep_distro}/${pkg}`.

### 4.5. `rosinstall_generator` boundary resolution
* Verified that generator functions like `get_package_names()`, `generate_rosinstall()`, and `get_recursive_dependencies()` recursively resolve dependencies across chained boundaries automatically without library modifications, since they rely on the updated `rosdistro` APIs.

---

## 5. Segregated Test Configs
Tests for Workflow 4 are located under the `tests/workflow_4/` directory:

* **Index**: [tests/workflow_4/index.yaml](../tests/workflow_4/index.yaml) (defines `base`, `derived_binary`, and `derived_source` distributions).
* **Base Distro**: [tests/workflow_4/base/distribution.yaml](../tests/workflow_4/base/distribution.yaml) (defines `turtlesim` in `base` distribution).
* **derived_binary**: [tests/workflow_4/derived_binary/distribution.yaml](../tests/workflow_4/derived_binary/distribution.yaml) (extends `base` via `binary_import`, and defines `new_package`).
* **derived_source**: [tests/workflow_4/derived_source/distribution.yaml](../tests/workflow_4/derived_source/distribution.yaml) (extends `base` via `source_rebuild`, and overrides `turtlesim` to version `0.3.10`).

---

## 6. Verification Commands Run inside Container
The tests are executed inside the isolated `ubuntu:noble` container using `docker/run_tests.sh`:

```bash
docker run --rm ros-distro-ext-test .venv/bin/python3 tests/workflow_4/test_workflow_4.py
```

### Script Assertions:
1. **derived_binary (binary_import)**:
   * Assert `turtlesim` (imported from parent) resolves to `ros-base-turtlesim`.
   * Assert `new_package` (defined locally) resolves to `ros-derived-binary-new-package`.
2. **derived_source (source_rebuild)**:
   * Assert `turtlesim` (rebuilt in derived distro) resolves to `ros-derived-source-turtlesim`.
3. **bloom release generator**:
   * Assert `bloom`'s `resolve_rosdep_key` resolves `turtlesim` to `['ros-base-turtlesim']` and `new_package` to `['ros-derived-binary-new-package']`.
4. **superflore ebuild generator**:
   * Assert `superflore` parses ebuild dependency mappings and formats them as `ros-base/turtlesim` and `ros-derived_binary/new_package` respectively.

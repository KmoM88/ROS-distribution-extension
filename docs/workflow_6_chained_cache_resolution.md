# Workflow 6: Chained Distribution Cache Resolution (Edge Case)

This document outlines the design, implementation steps, and verification scenarios for **Workflow 6: Chained Distribution Cache Resolution**.

---

## 1. Overview
* **Agent**: Toolchain Integrator Agent
* **Role**: Responsible for implementing chained cache generation and resolution mechanics to prevent cache file bloat and optimize loading performance.
* **Goal**: Support minimal distribution cache files for derived distributions and recursively load parent caches on demand when resolving dependency chains.

---

## 2. Design Specification

### A. Minimal Cache files
Under standard REP-143 overlay setups, running `rosdistro_build_cache` on a derived distribution generates a massive cache containing metadata for all inherited packages. To optimize workspace performance:
- The derived distribution's cache must be minimal, storing only the repositories and packages defined directly within the derived distribution file.
- If a consumer tool needs details on inherited packages, it must locate and load the parent caches recursively.

### B. Chained Cache Loader
When the `DistributionCache` class is instantiated to load a derived cache:
1. It reads the `extends` block in the cache file.
2. For each parent distribution, it resolves its cache path (either locally or via remote URL index) and loads the parent cache file.
3. The parent cache data is recursively merged into the active cache view in memory.

---

## 3. Implementation Steps

### Step 3.1: Modify `rosdistro_build_cache`
- **File**: `submodules/kmom88-rosdistro/src/rosdistro/build_cache.py`
- **Logic**:
  - Update cache generator to check if `dist_file.version >= 3` and has an `extends` block.
  - Exclude parent package metadata from the output cache file. Write only derived package entries.
  - Save the parent cache references (`extends` block) inside the output `rolling-cache.yaml` metadata.

### Step 3.2: Update Cache Loader in `rosdistro`
- **File**: `submodules/kmom88-rosdistro/src/rosdistro/distribution_cache.py`
- **Logic**:
  - Implement recursive cache resolution in the loader class.
  - Ensure that loading a derived cache automatically fetches and overlays parent cache contents in post-order.

---

## 4. Segregated Mock Configuration Setup
We will establish a mock cache baseline under `tests/workflow_6/`:

- **Index File**: `tests/workflow_6/index.yaml`
- **Base Distro**: `tests/workflow_6/base/distribution.yaml`
- **Derived Distro**: `tests/workflow_6/derived/distribution.yaml` (Extends `base` via `binary_import`).

---

## 5. Verification Commands
Tests will run inside the isolated Docker container:

```bash
docker run --rm ros-distro-ext-test .venv/bin/python3 tests/workflow_6/test_workflow_6.py
```

### Expected Test Assertions:
1. **Cache Size Assertion**: Assert that the generated derived cache file contains only derived repositories and does not duplicate base packages.
2. **Recursive Load Assertion**: Assert that `rosdistro.get_cached_distribution` loads base package metadata recursively and returns a combined, valid cache in memory.
3. **Tool Resolution**: Verify that `rosinstall_generator` resolves dependencies successfully by reading the chained caches.

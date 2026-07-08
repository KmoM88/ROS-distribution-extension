# Workflow 5: Mixed Chains & Multi-Parent Collisions (Edge Case)

This document outlines the design, implementation steps, and verification scenarios for **Workflow 5: Mixed Chains & Multi-Parent Collisions**.

---

## 1. Overview
* **Agent**: Toolchain Integrator Agent
* **Role**: Responsible for implementing precedence and collision resolution rules across multi-parent inheritance trees and mixed extension chains.
* **Goal**: Validate depth-first search (DFS) post-order inheritance resolution, verify proper package renaming depending on chain methods, and implement warnings/errors when package definition collisions occur.

---

## 2. Design Specification

### A. Precedence Rules (DFS Post-Order)
When a distribution file declares multiple parent distributions:
```yaml
extends:
  - distro_name: parent_a
    extension_method: binary_import
  - distro_name: parent_b
    extension_method: source_rebuild
```
The resolution follows a depth-first search (DFS) post-order traversal matching the order of declaration in `extends`. If a package exists in both parent chains, the first declared parent (`parent_a`) takes precedence.

### B. Mixed Chains Propagation
* If **Distribution A** extends **Distribution B** via `source_rebuild`, and **Distribution B** extends **Distribution C** via `binary_import`:
  * Packages defined in B are rebuilt and renamed as `ros-A-{pkg}`.
  * Packages imported into B from C via `binary_import` (which in B are references to `ros-C-{pkg}`) will be rebuilt as well into `ros-A-{pkg}` due to the transitive `source_rebuild` instruction, unless the package name is specifically blacklisted or masked.
* If the chain is reversed: A extends B via `binary_import`, and B extends C via `source_rebuild`:
  * Packages in B (rebuilt from C) are imported into A as binary packages (`ros-B-{pkg}`).

### C. Collision Warning System
If multiple parents define the same repository or package (e.g. both `parent_a` and `parent_b` release `turtlesim`), the parser must log a warning if no explicit override is declared in the child distribution file, prompting the developer to declare a masking rule or custom source reference.

---

## 3. Implementation Steps

### Step 3.1: Update `rosdistro` Parser
- **File**: `submodules/kmom88-rosdistro/src/rosdistro/__init__.py`
- **Logic**:
  - Update `_resolve_extends` recursive tree traversal. Ensure post-order traversal order is strictly maintained.
  - Track repository origin maps to identify package source collisions. If a repository key is overridden during merge from multiple parent branches, log a `CollisionWarning`.

### Step 3.2: Update `rosdep` Mappings
- **File**: `submodules/kmom88-rosdep/src/rosdep2/gbpdistro_support.py`
- **Logic**:
  - Traverse the resolved repository origins recursively to decide the binary package name prefix.
  - Resolve the correct package naming pattern dynamically depending on whether any step in the inheritance path specifies `source_rebuild`.

---

## 4. Segregated Mock Configuration Setup
We will establish a mock test baseline under `tests/workflow_5/`:

- **Index File**: `tests/workflow_5/index.yaml`
- **Root Distro**: `tests/workflow_5/root/distribution.yaml` (Defines `turtlesim` at version `0.3.9` and `std_msgs` at version `1.0.0`).
- **Parent A (binary_import)**: `tests/workflow_5/parent_a/distribution.yaml` (Extends `root` via `binary_import`).
- **Parent B (source_rebuild)**: `tests/workflow_5/parent_b/distribution.yaml` (Extends `root` via `source_rebuild`).
- **Child (multi-parent)**: `tests/workflow_5/child/distribution.yaml` (Extends both `parent_a` and `parent_b`).

---

## 5. Verification Commands
Tests will run inside the isolated Docker container:

```bash
docker run --rm ros-distro-ext-test .venv/bin/python3 tests/workflow_5/test_workflow_5.py
```

### Expected Test Assertions:
1. **Precedence Assertion**: Assert that child packages resolve using the precedence of `parent_a` first.
2. **Collision Warning**: Assert that loading the child distribution prints a collision warning for `turtlesim` since it is defined in both parent branches without an explicit override.
3. **Prefix Mappings**: Assert `rosdep` returns the correct binary naming prefix based on the mixed-chain propagation rules.

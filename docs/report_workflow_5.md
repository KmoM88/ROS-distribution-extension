# Workflow 5 Status Report: Mixed Chains & Multi-Parent Collisions

This report details the execution, configurations, results, and critical adoption insights of **Workflow 5: Mixed Chains & Multi-Parent Collisions**.

---

## 1. Objectives & Setup Criteria
The main objective of Workflow 5 was to extend the Version 3 distribution parser to support multiple parents and mixed inheritance chains. This includes:
1. **Precedence (DFS Post-Order)**: Ensuring that if multiple parents define the same package or repository, the first declared parent in the `extends` array takes precedence.
2. **Collision Warning System**: Logging clear warnings to notify developers if overlapping definitions exist in multiple parent branches without an explicit override.
3. **Mixed Chain Naming**: Propagating the `extension_method` correctly so that transitive dependencies are rebuilt/renamed if a `source_rebuild` is present in the path.

---

## 2. Submodule Modifications

### A. `rosdistro` (Parser Warnings and Re-mapping)
- **Collision Checking** ([distribution_file.py](../submodules/kmom88-rosdistro/src/rosdistro/distribution_file.py)): 
  - Checks if a repository or package being merged is already present in the active distribution.
  - If the repository or package was inherited from a previous parent, it prints a warning:
    `WARNING: Collision detected. Repository/Package '<name>' is defined in multiple parents ('<other_parent>' and '<parent_dist_file.name>'). Using definition from '<other_parent>'.`
- **Origin Re-mapping** ([distribution_file.py](../submodules/kmom88-rosdistro/src/rosdistro/distribution_file.py)):
  - If a package is inherited via `source_rebuild`, its `origin_distro` is overwritten to the current derived distribution name, ensuring downstream consumers prefix it as `ros-{derived}-{pkg}` instead of using the base namespace.

### B. `rosdep` (Editable Local Toggling)
- **Dependency Override** ([setup.py](../submodules/kmom88-rosdep/setup.py)):
  - Added a conditional dependency check for `ROSDEP_LOCAL_DEV`. If set to `'true'`, it resolves `rosdistro` dependency normally (utilizing the local editable directory) instead of fetching the remote git repo branch directly.

---

## 3. Added Verification Tests

### A. Isolated Unit Tests
- Added `test_multi_parent_precedence_and_collisions` to the `rosdistro` unit test suite [test_extends.py](../submodules/kmom88-rosdistro/test/test_extends.py).

### B. Segregated Integration Tests
- Structure defined under `tests/workflow_5/`:
  - **Index File**: [tests/workflow_5/index.yaml](../tests/workflow_5/index.yaml) (Registers mock index v4).
  - **Root Distro**: [tests/workflow_5/root/distribution.yaml](../tests/workflow_5/root/distribution.yaml) (Defines baseline `turtlesim` and `std_msgs`).
  - **Parent A (binary_import)**: [tests/workflow_5/parent_a/distribution.yaml](../tests/workflow_5/parent_a/distribution.yaml) (Declares `collision_pkg` at version `1.0.0`).
  - **Parent B (source_rebuild)**: [tests/workflow_5/parent_b/distribution.yaml](../tests/workflow_5/parent_b/distribution.yaml) (Declares `collision_pkg` at version `2.0.0`).
  - **Child (multi-parent)**: [tests/workflow_5/child/distribution.yaml](../tests/workflow_5/child/distribution.yaml) (Extends both parents).
- **Test Script** ([test_workflow_5.py](../tests/workflow_5/test_workflow_5.py)):
  - Asserts that `collision_repo` resolves to version `1.0.0` (matching the first parent, `parent_a`).
  - Asserts that all warnings for repository and package collisions are captured in stdout.
  - Asserts `rosdep` package resolution (resolving `std_msgs` to `ros-root-std-msgs` and `collision_pkg` to `ros-parent-a-collision-pkg`).

---

## 4. Verification Results

Running the containerized test suite via `bash docker/run_tests.sh` successfully executed the verification steps:

```bash
Running Workflow 5 Mixed Chains & Precedence Test...
Loading Workflow 5 index from: file:///workspace/tests/workflow_5/index.yaml
Query rosdistro index file:///workspace/tests/workflow_5/index.yaml
Add distro "child"
WARNING: Collision detected. Repository 'collision_repo' is defined in multiple parents ('parent_a' and 'parent_b'). Using definition from 'parent_a'.
WARNING: Collision detected. Repository 'std_msgs_repo' is defined in multiple parents ('root' and 'parent_b'). Using definition from 'root'.
WARNING: Collision detected. Repository 'turtlesim_repo' is defined in multiple parents ('root' and 'parent_b'). Using definition from 'root'.
Add distro "parent_a"
Add distro "parent_b"
Add distro "root"
Captured Warnings:
Loading child distribution...
WARNING: Collision detected. Repository 'collision_repo' is defined in multiple parents ('parent_a' and 'parent_b'). Using definition from 'parent_a'.
WARNING: Collision detected. Package 'collision_pkg' is defined in multiple parents ('parent_a' and 'parent_b'). Using definition from 'parent_a'.
WARNING: Collision detected. Repository 'std_msgs_repo' is defined in multiple parents ('root' and 'parent_b'). Using definition from 'root'.
WARNING: Collision detected. Package 'std_msgs' is defined in multiple parents ('root' and 'parent_b'). Using definition from 'root'.
WARNING: Collision detected. Repository 'turtlesim_repo' is defined in multiple parents ('root' and 'parent_b'). Using definition from 'root'.
WARNING: Collision detected. Package 'turtlesim' is defined in multiple parents ('root' and 'parent_b'). Using definition from 'root'.

std_msgs resolves to: ['ros-root-std-msgs']
collision_pkg resolves to: ['ros-parent-a-collision-pkg']
child_pkg resolves to: ['ros-child-child-pkg']
Workflow 5 verification test PASSED!
```

---

## 5. Development Pain Points & Adoption Challenges

Implementing and testing Workflow 5 exposed several critical hurdles for the general adoption of REP-2015:

### 1. Silent Editable Dependency Overwrites in PIP
* **Pain Point**: Pip cannot resolve a dependency that points directly to a git URL (`rosdistro @ git+https://...`) alongside a local editable version of the same package (`pip install -e`). In previous workflows, pip solved this by silently downloading the remote git version and overwriting the local editable installation. This meant that local code changes (such as parser updates) were silently discarded inside the testing container.
* **Adoption Insight**: Standardizing how downstream clients declare requirements is crucial. Direct git URL references in production dependency trees are highly discouraged. Instead, standard version requirements (e.g. `rosdistro >= 1.0.0`) must be used, allowing local checkouts or dev workspaces to overlay the dependency cleanly.

### 2. Package Object Indirection
* **Pain Point**: When merging repository layouts, `rosdistro` maps packages in `self.release_packages` as `Package` instances. Since `Package` objects only hold name string values, they do not inherit `origin_distro` or `extension_method` attributes from the repository.
* **Adoption Insight**: Looking up package origins requires resolving the package's parent repository name from the distribution's repository registry. Any parser changes must perform this indirection rather than expecting attributes on the package object directly.

### 3. Namespace Drift on Source Rebuilds
* **Pain Point**: If **Distribution A** source-rebuilds **Distribution B**, and **Distribution B** binary-imports **Distribution C**:
  * Since A is rebuilding, the namespace prefix of B's packages becomes `ros-A-*`.
  * If B's package has an `origin_distro` pointing to `C`, downstream clients would resolve B's package as `ros-C-*`, causing package resolution errors.
* **Adoption Insight**: The inheritance engine must automatically overwrite the package origin to the rebuilding distribution's namespace if `extension_method == 'source_rebuild'`.

### 4. Overlap Noise in Common Ancestors
* **Pain Point**: When two parent distributions (e.g., `parent_a` and `parent_b`) both extend the same base `root`, they both inherit `std_msgs` and `turtlesim` from it. When `child` extends both, they are flagged as collisions even though they originate from the exact same common ancestor.
* **Adoption Insight**: To prevent warning spam, the collision engine should check if the colliding repositories originate from the same `origin_distro`. If the origin distros are identical, the warning should be suppressed since the inheritance tree resolved them to the same source.

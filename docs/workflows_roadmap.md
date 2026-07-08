# Project Workflows & Testing Roadmap (REP-2015)

This document details the development workflows, test specifications, and validation plans for implementing and verifying **REP-2015: ROS Distribution Extensions** in this workspace.

## Feasibility & Implementation Assessment Goal
The primary objective of this project is to evaluate the implementability of REP-2015 across the ROS infrastructure ecosystem. This involves:
- Identifying edge cases and functional limitations in the proposed specification.
- Extending and modifying the upstream forks (`rosdistro`, `rosdep`, `rosinstall_generator`, `ros_buildfarm`, `bloom`, and `superflore`) to support the version 3 distribution schema.
- Documenting the advances made in each fork and compiling a final report that highlights areas that are particularly difficult to implement or that clash with the underlying philosophy of the existing tools.

> [!IMPORTANT]
> **Branching & Container Policies**:
> 1. All tool testing, dry-runs, and execution must run in the isolated Docker container (`ros-distro-ext-test`).
> 2. When moving forward beyond testing current status (i.e. modifying submodules/code for Workflows 3 and 4), development must be carried out in a specific `feature/testing` branch in each individual tool fork (`rosdistro`, `rosdep`, `rosinstall_generator`, `ros_buildfarm`).

---

## Workflow 1: Repository Setup & Environment Management
**Agent**: Environment Manager Agent  
**Purpose**: Set up the baseline workspace structure, manage development forks, and prepare mock configuration environments.

### Tasks
1. **Fork Critical Repositories**: Ensure origin forks are created under the `KmoM88` organization/account for:
   * `rosdistro`
   * `rosinstall_generator`
   * `ros_buildfarm`
   * `rosdep`
   * `bloom`
   * `superflore`
2. **Submodule Setup**: Add and initialize these forks under `submodules/kmom88-<tool_name>`.
3. **Docker Environment Setup**:
   * Define the testing `docker/Dockerfile` (based on `ubuntu:noble`) that creates an isolated virtual environment and installs submodules in editable mode.
   * Create a test runner script (`docker/run_tests.sh`) to automate container building and test execution.
4. **Mock Environment baseline**: Setup a test configuration area `tests/workflow_1/` with mock `index.yaml` and `distribution.yaml` files.

### Verification Criteria
* Submodule git state is clean: `git status` reports no untracked or dirty submodules.
* The Docker image compiles successfully, and all packages (`rosdistro`, `rosdep`, etc.) are correctly installed in editable mode inside the container.
* Test files are readable on the filesystem under `tests/workflow_1/`.

---

## Workflow 2: Testing Current Behavior (Baseline)
**Agent**: Baseline QA Agent  
**Purpose**: Ensure the current, unmodified codebase parses and processes standard files correctly without breaking changes.

### Tasks
1. **Segregated Config**: Set up separate configuration files under `tests/workflow_2/` containing the base distribution file and `overlay.yaml`.
2. **Verify REP-143 Overlay/Merge parsing**:
   * Load the multi-file index and verify `rosdistro.get_distribution_file()` merges overlays cleanly.
3. **Docker-based testing**:
   * Build the Docker image `ros-distro-ext-test` using `docker/Dockerfile`.
   * Run the container via `docker/run_tests.sh` to initialize `rosdep` and run tests in an isolated, reproducible `ubuntu:noble` container.
4. **Toolchain verification**:
   * Validate `rosdistro_build_cache` outputs the cache.
   * Validate `rosinstall_generator` generates `.rosinstall` entries.
   * Validate `rosdep` database queries execute successfully in the container.

### Verification Criteria
* All tests pass successfully inside the Docker container.
* Overrides in `overlay.yaml` (e.g. `status` changes) are correctly merged and verified by `test_workflow_2.py`.

---

## Workflow 3: Testing REP-2015 Proposals (Distribution File Version 3)
**Agent**: Extension Parser Agent  
**Purpose**: Introduce parser support for Version 3 distribution files (`extends` and `dependencies`).

### Tasks
1. **Develop Parser for `extends`**:
   * Update parser rules to read the `extends` block:
     ```yaml
     extends:
       - distro_name: base_distro
         index_url: file:///path/to/index.yaml
         extension_method: binary_import
     ```
2. **Develop Parser for `dependencies`**:
   * Read the `dependencies` block (e.g. `rosdep_sources_list_urls` and `rosdep_minimum_target_platforms`).
3. **Platform Check & Warning system**:
   * Implement validation checking if the derived distribution targets an OS/codename not listed in the parent's target platforms. Generate warnings during parsing.
4. **Loop/Circular Inheritance Detection**:
   * Implement detection that raises an exception if a distribution extends itself or forms a cycle.

### Verification Criteria
* Test suite running on Version 3 files passes.
* Parsing a cyclic extends file fails with a clear error.
* Mismatched target platforms print a warning.

---

## Workflow 4: Testing Extension Methods & Toolchain Integration
**Agent**: Toolchain Integrator Agent  
**Purpose**: Update client tools to support `binary_import` and `source_rebuild` runtime behaviors.

### Tasks
1. **Verify `binary_import` Behavior**:
   * Test that upstream packages are installed to `/opt/ros/{upstream_distro}` and named `ros-{upstream_distro}-{package}`.
   * Downstream packages must reference the upstream directories transparently.
2. **Verify `source_rebuild` Behavior**:
   * Test that packages are rebuilt, renamed to `ros-{derived_distro}-{package}`, and installed into `/opt/ros/{derived_distro}`.
   * Verify package overriding/masking (derived packages replace upstream packages of the same name).
3. **Tool Integration**:
   * **rosdep**: Update to query package mappings from parent distributions recursively.
   * **rosinstall_generator**: Traverse across distro boundaries when fetching package sources.
   * **ros_buildfarm**: Leverage chained caches to fetch release metadata.

### Verification Criteria
* Integration tests verify correct paths are generated for both import modes.
* Resolving a package override retrieves the derived package rather than the upstream package.

---

## Workflow 5: Testing Mixed Chains & Multi-Parent Collisions (Edge Case)
**Agent**: Toolchain Integrator Agent  
**Purpose**: Verify resolution precedence and mixed extension methods (`binary_import` + `source_rebuild`) across multi-parent distribution layouts.

### Tasks
1. **Config Multi-Parent Layout**: Set up an index where a child distribution extends multiple parents with different extension methods.
2. **Precedence Logic Checking**:
   * Verify that package resolving follows depth-first search order.
   * Verify that packages are resolved to the correct system binary package name depending on their source distribution's extension method in the mixed inheritance chain.
3. **Collision Warnings**:
   * Implement warnings if different base distributions define conflicting packages and no override is present in the derived distribution.

### Verification Criteria
* Tests verify that the first declared parent takes precedence.
* Packages in mixed chains resolve to the correct binary name pattern dynamically.

---

## Workflow 6: Chained Distribution Cache Resolution (Edge Case)
**Agent**: Toolchain Integrator Agent  
**Purpose**: Avoid cache duplication and enable consumer tools to load and resolve distribution caches incrementally across distribution boundaries.

### Tasks
1. **Segregated Cache Generation**:
   * Configure `rosdistro_build_cache` to generate isolated cache files for derived distributions containing only their own unique packages.
2. **Implement Chained Cache Loaders**:
   * Update the `DistributionCache` loader in `rosdistro` to recursively load parent cache files if an `extends` block is found.
3. **Verify Tool Integration**:
   * Ensure `rosinstall_generator` can resolve complete dependency trees by reading the chained caches recursively.

### Verification Criteria
* Cache files for derived distributions are minimal and contain no duplicated base package metadata.
* Dependency resolution runs successfully using the chained caches.

---

## Workflow 7: Feasibility Report & Downstream Integration Assessment
**Agent**: Toolchain Integrator Agent  
**Purpose**: Document all advances, edge cases, implementation difficulties, and philosophical conflicts encountered during integration with the downstream ROS release/packaging toolchain.

### Tasks
1. **Analyze Downstream Tools**:
   * Verify how `bloom` handles package releasing and key resolution under derived distribution environments.
   * Verify how `superflore` generates ebuilds, bitbake recipes, and nix expressions for packages targeting derived distributions, addressing dependency namespace issues.
2. **Document Implementation Roadblocks**:
   * Identify features of REP-2015 that are difficult to implement without major architectural refactoring of the parent ROS infrastructure codebases.
   * Detail any philosophical differences (e.g. how tools assume a single distribution prefix, or how they handle isolated package builds).
3. **Compile Final Summary**:
   * Write a comprehensive report detailing the status of each fork, the implementation completeness, and recommendations for standardizing REP-2015 version 3 distribution files.

### Verification Criteria
* A final markdown document detailing the feasibility analysis and advances is saved in the workspace.


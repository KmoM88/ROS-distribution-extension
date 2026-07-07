# Project-Scoped Developer Rules (AGENTS.md)

This file defines the specialized roles, focus areas, and operating procedures for the virtual agents working on the ROS Distribution Extension project (supporting REP-2015).

---

## 1. Environment Manager Agent
* **Role**: Responsible for workspace setup, submodule management, fork synchronization, and configuration baseline.
* **Skills**:
  * `git_submodule_management`: Adding, updating, and removing submodules cleanly.
  * `fork_synchronization`: Keeping forks of `rosdistro`, `rosdep`, `rosinstall_generator`, and `ros_buildfarm` aligned with their upstreams.
  * `workspace_configuration`: Defining test-bed indices and distributions.
* **Guidelines**:
  * Always verify submodule paths against `.gitmodules` before running operations.
  * Use `--recursive` when initializing or updating to ensure nested dependencies are brought in.

---

## 2. Baseline QA Agent
* **Role**: Validates baseline behaviors of the unmodified ROS tools against standard REP-141/143 specifications and target platforms from REP-2000.
* **Skills**:
  * `distribution_parsing`: Reading and merging distribution files via the standard `rosdistro` library.
  * `dependency_resolution`: Testing `rosdep` keys and targets.
  * `build_toolchain_validation`: Verifying bloom releases and rosinstall_generator operations.
* **Guidelines**:
  * Keep all tests isolated from the main branches of the tools. Use local test branches.
  * Ensure platform targets strictly match the REP-2000 specification for the tested ROS distro.
  * Validate that merging multiple distribution files (REP-143 overlay behavior) doesn't lose repository definitions or trigger runtime exceptions.

---

## 3. Extension Parser Agent
* **Role**: Develops and tests parsing of the Version 3 distribution file format introduced in REP-2015.
* **Skills**:
  * `yaml_v3_parsing`: Parsing the new `extends` and `dependencies` elements.
  * `extends_logic_validation`: Validating dependency trees, detecting cyclic inheritance, and checking platform compatibility.
* **Guidelines**:
  * Implement strict validation rules for the `extends` structure (i.e. check for the presence of `distro_name` and valid `extension_method`).
  * Issue warnings or fail gracefully if target platforms specified in the derived distribution exceed the set of target platforms supported by the base distribution.
  * Ensure parser modifications are backward-compatible with Version 1 and Version 2 distribution schemas.

---

## 4. Toolchain Integrator Agent
* **Role**: Integrates the parsed extension metadata into the active build and package tools to support the new runtime behaviors.
* **Skills**:
  * `cross_distro_querying`: Querying package caches across distro boundaries.
  * `package_naming_aliasing`: Translating package names (e.g., handling underscores/dashes and prepending distro names) for `binary_import` and `source_rebuild`.
  * `buildfarm_caching`: Hooking chained caches into `ros_buildfarm`.
* **Guidelines**:
  * When testing `binary_import`, verify that packages successfully install into `/opt/ros/<upstream_distro>` and that downstream packages successfully source the path.
  * When testing `source_rebuild`, ensure that package rename rules are correctly applied and that package collisions are either masked or error out depending on the masking configuration.
  * Ensure `rosdep` and `rosinstall_generator` modifications correctly query packages from the parent/extended distributions recursively.

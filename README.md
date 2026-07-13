# ROS Distribution Extension (REP-2015 Case Study)

This repository serves as a validation test-bed and case study for [REP-2015 (ROS Distribution Extensions)](https://github.com/openrobotics/reps/blob/rosdistro_extension/_posts/rep-2015.md). It implements the proposed extends/overlay specification across the primary ROS packaging, release, and dependency management tools.

---

## Overview of Accomplishments
We successfully extended and validated the ROS distribution overlay infrastructure across six distinct workflows:

| Workflow | Description | Status & Reports |
| :--- | :--- | :--- |
| **Workflow 1** | Implemented the Version 3 distribution parser schema supporting `extends` and `dependencies` elements in `rosdistro`. | [Report](docs/report_workflow_1.md) \| [Tests](tests/workflow_1/) |
| **Workflow 2** | Implemented distribution overlay merging (`merge_extends`) allowing derived distributions to inherit and override repositories and packages. | [Report](docs/report_workflow_2.md) \| [Tests](tests/workflow_2/) |
| **Workflow 3** | Enforced target platform compatibility checks and recursive cycle/circular inheritance detection in `rosdistro`. | [Report](docs/report_workflow_3.md) \| [Tests](tests/workflow_3/) |
| **Workflow 4** | Integrated package name and category translation across boundary layers for binary and source distribution methods in `rosdep`, `bloom`, and `superflore`. | [Report](docs/report_workflow_4.md) \| [Tests](tests/workflow_4/) |
| **Workflow 5** | Supported multiple parents, DFS post-order precedence ordering, repository/package collision warning logs, and namespace re-mapping in `source_rebuild` chains. | [Report](docs/report_workflow_5.md) \| [Tests](tests/workflow_5/) |
| **Workflow 6** | Implemented minimal disk cache compilation in `rosdistro_build_cache` and recursive in-memory chained cache resolution in cache loaders. | [Report](docs/report_workflow_6.md) \| [Tests](tests/workflow_6/) |

---

## Submodule Forks
The modifications are integrated into the respective tool submodules. We maintain and test against the following forks:

* **[rosdistro](https://github.com/KmoM88/rosdistro)**: Extended parser version 3 format, precedence rules, cyclic loops detection, collision warnings, and chained cache resolutions.
* **[rosdep](https://github.com/KmoM88/rosdep)**: Added multi-distro query resolutions and toggled local editable installations for test isolation.
* **[rosinstall_generator](https://github.com/KmoM88/rosinstall_generator)**: Sourced packages recursively across distro boundaries using chained caches.
* **[ros_buildfarm](https://github.com/KmoM88/ros_buildfarm)**: Handles chained cache generations and naming formats.
* **[bloom](https://github.com/KmoM88/bloom)**: Sourced custom Debian package name maps matching derived-distro prefixes.
* **[superflore](https://github.com/KmoM88/superflore)**: Formats Gentoo Ebuild categories dynamically as `ros-{distro}/{pkg}` based on package origin.

---

## Verification Suite

To validate the implementation in a clean, reproducible environment, we provide a containerized test suite that runs all submodule unit tests and integration tests.

### Prerequisites
- Docker (installed and running)

### Running the Tests
Execute the test runner script from the root of the repository:
```bash
bash docker/run_tests.sh
```

This script will:
1. Build the isolated testing container (`ros-distro-ext-test`).
2. Run all six integration workflow verification test scripts (under `tests/`).
3. Run the pytest suites for all modified submodules (`rosdistro`, `rosdep`, `rosinstall_generator`, `ros_buildfarm`, `superflore`).
4. Output the results to the terminal.

---

## Documentation & Analysis
Detailed analysis, roadmap specifications, and feasibility reports are available under the `docs/` folder:
- [Roadmap & Test Specifications](docs/workflows_roadmap.md)
- [REP-2015 Case Study & Final Summary Report](docs/rep_2015_edge_cases_and_adoption.md)


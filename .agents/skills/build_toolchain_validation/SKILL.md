---
name: Build Toolchain Validation
description: Skill to validate source checkout and release builds via rosinstall_generator and bloom.
---

# Build Toolchain Validation

This skill ensures the unmodified tools work correctly as submodules before we apply extensions.

## Procedures

### Generate rosinstall File
Verify `rosinstall_generator` compiles recursive workspace files:
```bash
rosinstall_generator ros_tutorials --rosdistro rolling --deps --tar > baseline.rosinstall
```

### Dry-run Bloom Release
Simulate package releasing on local repositories to verify baseline tagging behavior:
```bash
bloom-release --track rolling --rosdistro rolling --dry-run <package_name>
```

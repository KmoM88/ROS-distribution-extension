---
name: Extends Logic Validation
description: Skill to validate inheritance hierarchies, detect circular extends, and verify platform compatibility.
---

# Extends Logic Validation

This skill ensures that inheritance rules defined in REP-2015 are strictly followed.

## Rules to Enforce

### 1. Loop Detection
Verify that no distribution extends itself directly or transitively:
* If Distro C extends Distro B, and Distro B extends Distro A:
  * Ensure A does not extend C or B.
  * Throw a `CircularInheritanceError` if a loop is detected.

### 2. Platform Warning
A derived distribution's target platforms must be a subset of (or compatible with) the base distribution's targets.
* Compare `rosdep_minimum_target_platforms` of the child against the parent.
* Issue a warning (or raise an exception depending on strict mode) if the child targets platforms not supported by the parent.
```python
def check_platform_compatibility(child_platforms, parent_platforms):
    for platform in child_platforms:
        if platform not in parent_platforms:
            print(f"WARNING: Target platform {platform} is not supported by parent.")
```

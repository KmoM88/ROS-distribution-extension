---
name: Package Naming & Aliasing
description: Skill to handle name translation, package masking, and target paths for binary_import and source_rebuild.
---

# Package Naming & Aliasing

This skill implements the binary renaming rules and dependency aliases defined in REP-2015.

## Specifications

### Binary Import (binary_import)
* Upstream packages preserve their original binary name: `ros-{upstream_distro}-{package_name}` (with underscores changed to dashes).
* Installation target remains: `/opt/ros/{upstream_distro}`.
* Downstream packages must reference the upstream dependency name explicitly.

### Source Rebuild (source_rebuild)
* Packages are rebuilt and renamed: `ros-{derived_distro}-{package_name}`.
* Installation target changes to: `/opt/ros/{derived_distro}`.
* Collisions: If a package is overridden in the derived distribution, the derived version masks the upstream version.

```python
def get_binary_package_name(distro_name, package_name, method="binary_import", upstream_distro=None):
    clean_name = package_name.replace('_', '-')
    if method == "binary_import" and upstream_distro:
        return f"ros-{upstream_distro}-{clean_name}"
    return f"ros-{distro_name}-{clean_name}"
```

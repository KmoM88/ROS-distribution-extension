---
name: Dependency Resolution
description: Skill to validate dependency resolution using the rosdep command and API.
---

# Dependency Resolution

This skill describes how to run dependency queries, register database entries, and verify packages against target platforms.

## Commands Reference

### Install Dependencies for Workspace
Verify that `rosdep` can resolve dependencies for checked-out packages:
```bash
rosdep install --from-paths src --ignore-src -r -y
```

### Validate Specific Rosdep Key
Check the resolved apt/yum package name for a specific key under target platforms:
```bash
rosdep resolve <rosdep_key> --os=<os_name>:<os_version>
# Example:
rosdep resolve python3-numpy --os=ubuntu:noble
```

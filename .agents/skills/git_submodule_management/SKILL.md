---
name: Git Submodule Management
description: Skill to manage Git submodules in the ROS-distribution-extension workspace.
---

# Git Submodule Management

This skill covers the basic workflows for ensuring submodules are properly initialized, updated, and cleaned up in this project.

## Standard Procedures

### Initialize and Update
When setting up or updating submodules:
```bash
git submodule update --init --recursive
```

### Check Status
Verify the current commit checked out for each submodule:
```bash
git submodule status
```

### Remove a Submodule Cleanly
If you need to remove a submodule (e.g., `ros_buildfarm` or any other):
1. De-register the submodule:
   ```bash
   git submodule deinit -f submodules/<submodule_path>
   ```
2. Remove the submodule from git tracking and working tree:
   ```bash
   git rm -f submodules/<submodule_path>
   ```
3. Remove the Git internal cache directory:
   ```bash
   rm -rf .git/modules/submodules/<submodule_path>
   ```

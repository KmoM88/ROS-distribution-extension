---
name: Fork Synchronization
description: Skill to synchronize the forked repository submodules with their respective upstreams.
---

# Fork Synchronization

This skill handles updating the development forks from official upstream repositories (e.g., `ros/rosdistro`, `ros-infrastructure/rosdep`, etc.).

## Standard Procedures

### Adding Upstream Remotes
To pull latest changes from the official upstreams:
1. Navigate to the submodule directory (e.g., `submodules/kmom88-rosdistro`):
   ```bash
   git remote add upstream https://github.com/ros/rosdistro.git
   ```
2. Fetch and merge upstream changes:
   ```bash
   git fetch upstream
   git merge upstream/master
   ```

### Pushing to the Fork
Once merged, push the updated master/main branch to the `KmoM88` origin fork:
```bash
git push origin master
```

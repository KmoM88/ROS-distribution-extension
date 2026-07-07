---
name: Cross-Distro Querying
description: Skill to query packages and dependencies recursively across multiple chained distribution caches.
---

# Cross-Distro Querying

This skill enables querying packages that are defined in parent distributions transparently from the derived distribution cache.

## Execution Pattern

### Recursive Cache Traversal
When querying a package name in the derived distribution:
1. Search in the local derived distribution file.
2. If not found, check the base distribution listed under `extends`.
3. Recurse up the chain until the package is located or the root distribution is reached.
4. Raise `PackageNotFoundError` if the package does not exist in any layer.

```python
def find_package_in_extended_dist(dist_file, package_name):
    if package_name in dist_file.repositories:
        return dist_file.repositories[package_name]
    for ext in dist_file.extends:
        parent_dist = load_parent_dist(ext)
        result = find_package_in_extended_dist(parent_dist, package_name)
        if result:
            return result
    return None
```

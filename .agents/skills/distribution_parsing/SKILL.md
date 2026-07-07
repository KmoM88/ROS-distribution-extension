---
name: Distribution Parsing
description: Skill to parse ROS index and distribution files using the rosdistro library.
---

# Distribution Parsing

This skill details how to parse standard distribution files (Version 1 and 2) using the `rosdistro` library, ensuring that multiple distribution files (overlays) are merged correctly.

## API Usage Reference

### Loading the Index File
Use python to load the index from a local file path or URL:
```python
import rosdistro
index = rosdistro.get_index("file:///path/to/index.yaml")
```

### Retrieving and Merging Distribution Files
Use `get_distribution_file()` to fetch the merged distribution structure:
```python
# Fetches and merges all distribution files listed for the distro key
dist_file = rosdistro.get_distribution_file(index, 'rolling')
print(dist_file.repositories.keys())
```

### Checking Underlying Distribution Files
Access individual distribution files explicitly:
```python
files = rosdistro.get_distribution_files(index, 'rolling')
for f in files:
    print(f.repositories.keys())
```

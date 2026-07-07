---
name: YAML v3 Parsing
description: Skill to parse the extends and dependencies elements of the Version 3 distribution file.
---

# YAML v3 Parsing

This skill outlines how to implement and test parser support for the new structures in REP-2015.

## Data Structures (Draft)

### Version 3 Distribution File
Under Version 3, the schema is extended with:
```yaml
# distribution.yaml
type: distribution
version: 3
extends:
  - distro_name: rolling
    index_url: file:///path/to/base_index.yaml # Optional
    extension_method: binary_import # Or 'source_rebuild'
dependencies:
  - rosdep_sources_list_urls:
      - https://raw.githubusercontent.com/ros/rosdistro/master/rosdep/base.yaml
    rosdep_minimum_target_platforms:
      - ubuntu:noble
      - debian:bookworm
```

## Parsing Routine (Target code pattern)
Ensure `rosdistro` parser processes these elements during loading:
```python
def parse_distribution_v3(data):
    extends = data.get('extends', [])
    dependencies = data.get('dependencies', [])
    # Validate and return parsed entities
```

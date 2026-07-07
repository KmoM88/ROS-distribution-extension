---
name: Workspace Configuration
description: Skill to establish target environments, distribution files, and testing baseline structures.
---

# Workspace Configuration

This skill outlines how to configure test beds, directory paths, and index files for evaluating REP-2015 extensions.

## Standard Procedures

### Directory Structure for Testing
Create a designated test structure in the root of the workspace or in temporary testing folders:
* `tests/baseline/`: For standard REP-141/143 indices and distribution files.
* `tests/extension/`: For Version 3 index and distribution files containing `extends` elements.

### Example Baseline Configuration (REP-143 Index version 3)
Define a minimal index file (`index.yaml`) pointing to standard files:
```yaml
%YAML 1.1
---
distributions:
  rolling:
    distribution:
      - tests/baseline/rolling/distribution.yaml
type: index
version: 3
```

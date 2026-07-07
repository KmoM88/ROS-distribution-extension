---
name: Buildfarm Caching
description: Skill to handle chained cache generation and resolution in ros_buildfarm.
---

# Buildfarm Caching

This skill configures and verifies cache chains in `ros_buildfarm`, ensuring builds in derived distributions correctly reference pre-built binaries from parent distributions.

## Procedures

### Cache Generation
Generate individual caches for the base distribution first:
```bash
rosdistro_build_cache file:///path/to/base/index.yaml rolling --ignore-errors
```

### Cache Chaining
Configure the derived build cache to load and merge the base cache rather than recalculating the metadata for base packages:
1. Identify the cache locations from the index `release_cache` property.
2. Read and overlay the derived cache on top of the parent cache.
3. Validate that package signatures are preserved.

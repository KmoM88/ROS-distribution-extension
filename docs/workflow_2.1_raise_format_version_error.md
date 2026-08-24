# Workflow 2.1: Raise FormatVersionError in rosdistro

This document details the design, changes, and verification test cases for implementing **Workflow 2.1: Raise FormatVersionError in rosdistro**.

The goal is to replace the generic `AssertionError` raised when checking file format versions inside the `rosdistro` parser with a custom, structured `FormatVersionError` exception class. This enables downstream consumer applications (like `rosdep`) to safely catch and handle version incompatibilities.

To isolate this change and model it for a clean pull request, we will create a new git branch `feature/format-version-error` in the `rosdistro` submodule originating directly from its upstream `master` branch (without any of the REP-2015 version 3 parser changes).

---

## Proposed Changes

### 1. Submodule Workspace Setup
* **Branch Creation**: Check out a new branch `feature/format-version-error` in `submodules/kmom88-rosdistro` originating from `master`.

---

### 2. rosdistro Submodule Changes

#### [MODIFY] [__init__.py](../submodules/kmom88-rosdistro/src/rosdistro/__init__.py)
* Define the new exception class:
  ```python
  class FormatVersionError(Exception):
      def __init__(self, file_type, version, supported_versions, file_name=None):
          self.file_type = file_type
          self.version = version
          self.supported_versions = supported_versions
          self.file_name = file_name
          msg = "Unable to handle '%s' format version '%s'" % (file_type, str(version))
          if file_name:
              msg += " for '%s'" % file_name
          msg += ", please update rosdistro (e.g. on Ubuntu/Debian use: sudo apt-get update && sudo apt-get install --only-upgrade python-rosdistro)"
          super(FormatVersionError, self).__init__(msg)
  ```

#### [MODIFY] [index.py](../submodules/kmom88-rosdistro/src/rosdistro/index.py)
* Replace version assertions with raising `FormatVersionError`:
  ```python
  if int(data['version']) not in [2, 3, 4]:
      raise FormatVersionError(Index._type, data['version'], [2, 3, 4])
  ```

#### [MODIFY] [distribution_file.py](../submodules/kmom88-rosdistro/src/rosdistro/distribution_file.py)
* Replace version assertions with raising `FormatVersionError`:
  ```python
  if int(data['version']) not in [1, 2]:
      raise FormatVersionError(DistributionFile._type, data['version'], [1, 2], self.name)
  ```

#### [MODIFY] [source_file.py](../submodules/kmom88-rosdistro/src/rosdistro/source_file.py)
* Replace version assertions with raising `FormatVersionError` for `SourceFile`.

#### [MODIFY] [release_file.py](../submodules/kmom88-rosdistro/src/rosdistro/release_file.py)
* Replace version assertions with raising `FormatVersionError` for `ReleaseFile`.

#### [MODIFY] [doc_file.py](../submodules/kmom88-rosdistro/src/rosdistro/doc_file.py)
* Replace version assertions with raising `FormatVersionError` for `DocFile`.

#### [MODIFY] [release_build_file.py](../submodules/kmom88-rosdistro/src/rosdistro/release_build_file.py)
* Replace version assertions with raising `FormatVersionError` for `ReleaseBuildFile`.

#### [MODIFY] [source_build_file.py](../submodules/kmom88-rosdistro/src/rosdistro/source_build_file.py)
* Replace version assertions with raising `FormatVersionError` for `SourceBuildFile`.

#### [MODIFY] [doc_build_file.py](../submodules/kmom88-rosdistro/src/rosdistro/doc_build_file.py)
* Replace version assertions with raising `FormatVersionError` for `DocBuildFile`.

#### [MODIFY] [distribution_cache.py](../submodules/kmom88-rosdistro/src/rosdistro/distribution_cache.py)
* Replace version assertions with raising `FormatVersionError` for `DistributionCache`.

#### [MODIFY] [release_cache.py](../submodules/kmom88-rosdistro/src/rosdistro/release_cache.py)
* Replace version assertions with raising `FormatVersionError` for `ReleaseCache`.

---

## Verification Plan

### Automated Tests
We will add a new test case in `submodules/kmom88-rosdistro/test/test_version_error.py` that verifies:
1. Loading an index file with an unsupported version throws `FormatVersionError`.
2. Loading a distribution file with an unsupported version throws `FormatVersionError`.
3. Running `pytest` inside the `rosdistro` submodule container to ensure all existing test suites pass.

```bash
# Executing within the docker container:
pytest submodules/kmom88-rosdistro
```

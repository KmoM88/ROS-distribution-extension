# Workflow 2.1 Status Report: Raise FormatVersionError in rosdistro

This report details the execution, configurations, and test results of **Workflow 2.1: Raise FormatVersionError in rosdistro**.

---

## 1. Objectives & Setup Criteria
The main objective of Workflow 2.1 was to replace the generic `AssertionError` raised when checking file format versions inside the `rosdistro` parser with a custom, structured `FormatVersionError` exception class. 

This enables downstream consumer applications (like `rosdep`) to safely catch and handle version incompatibilities, improving overall error handling and logging.

### Design Requirements:
1. **Branch Isolation**: The changes are implemented on a dedicated clean branch (`feature/format-version-error`) in `submodules/kmom88-rosdistro` originating from `master`, without any of the REP-2015 version 3 parser changes.
2. **Descriptive Exception**: The new `FormatVersionError` class inherits from `Exception` and provides structured fields (`file_type`, `version`, `supported_versions`, `file_name`) to convey precise version details to callers.
3. **Comprehensive Refactoring**: Replace format version assertions across all parsing and validation modules.

---

## 2. Implemented Exception Design
The custom exception `FormatVersionError` is defined in [src/rosdistro/__init__.py](../submodules/kmom88-rosdistro/src/rosdistro/__init__.py):

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

---

## 3. Code Modifications
All files checking format versions have been updated to raise `FormatVersionError`:

* **`index.py`**: Raises error when version is not in `[2, 3, 4]`.
* **`distribution_file.py`**: Raises error when version is not in `[1, 2]`.
* **`source_file.py`**: Raises error when version is not `1`.
* **`release_file.py`**: Raises error when version is not `1`.
* **`doc_file.py`**: Raises error when version is not `1`.
* **`release_build_file.py`**: Raises error when version is not `1`.
* **`source_build_file.py`**: Raises error when version is not `1`.
* **`doc_build_file.py`**: Raises error when version is not `1`.
* **`distribution_cache.py`**: Raises error when version is not `2`.
* **`release_cache.py`**: Raises error when version is not `2`.

---

## 4. Verification Results

We verified that the newly implemented exception behaves correctly by adding unit tests in [test_version_error.py](../submodules/kmom88-rosdistro/test/test_version_error.py).

Running the unit test suite inside the submodule local virtual environment succeeded:

```bash
test/test_version_error.py ..                                            [100%]
============================== 2 passed in 0.07s ===============================
```

Additionally, all 54 existing tests in the `rosdistro` test suite pass successfully:
```bash
======================== 54 passed, 1 warning in 14.35s ========================
```

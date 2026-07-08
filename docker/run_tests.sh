#!/bin/bash
set -e

# Get workspace directory
WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$WORKSPACE_DIR"

echo "Building Docker container for isolated testing..."
docker build -t ros-distro-ext-test -f docker/Dockerfile .

echo "=========================================================="
echo "Running tests inside the isolated Docker container..."
echo "=========================================================="

docker run --rm ros-distro-ext-test bash -c "
set -e

echo 'Running Workflow 1 Python Parsing Test...'
.venv/bin/python3 tests/workflow_1/test_workflow_1.py

echo 'Running Workflow 2 Python Parsing & Overlay Merge Test...'
.venv/bin/python3 tests/workflow_2/test_workflow_2.py

echo 'Running Workflow 3 Python Parsing & extends/dependencies Test...'
.venv/bin/python3 tests/workflow_3/test_workflow_3.py

echo 'Running Workflow 4 Python Package Name Mapping Test...'
.venv/bin/python3 tests/workflow_4/test_workflow_4.py

echo 'Running internal rosdistro pytest suite...'
(cd submodules/kmom88-rosdistro && ../../.venv/bin/pytest test/)

echo 'Running internal rosdep pytest suite...'
(export PATH=/workspace/.venv/bin:$PATH && cd submodules/kmom88-rosdep && ../../.venv/bin/pytest test/)

echo 'Running internal rosinstall_generator pytest suite...'
(cd submodules/kmom88-rosinstall_generator && ../../.venv/bin/pytest test/)

echo 'Running internal ros_buildfarm pytest suite...'
(cd submodules/kmom88-ros_buildfarm && ../../.venv/bin/pytest test/test_repo.py test/test_create_workspace_archive.py test/test_package_naming.py)

echo 'Running internal superflore pytest suite...'
(cd submodules/kmom88-superflore && ../../.venv/bin/pytest tests/)

echo 'Generating local Cache for Workflow 2...'
.venv/bin/rosdistro_build_cache file:///workspace/tests/workflow_2/index.yaml rolling

echo 'Moving generated cache files to tests/workflow_2/'
mv rolling-cache.yaml* tests/workflow_2/

echo 'Running rosinstall_generator turtlesim test...'
ROSDISTRO_INDEX_URL=file:///workspace/tests/workflow_2/index.yaml .venv/bin/rosinstall_generator turtlesim --rosdistro rolling --tar

echo 'Running rosdep database dump test...'
ROSDISTRO_INDEX_URL=file:///workspace/tests/workflow_2/index.yaml .venv/bin/rosdep db | head -n 20

echo 'All isolated container tests PASSED successfully!'
"

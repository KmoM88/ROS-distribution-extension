#!/bin/bash
set -e

TARGET="${1:-all}"

# Get workspace directory
WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$WORKSPACE_DIR"

echo "Building Docker container for isolated testing..."
docker build -t ros-distro-ext-test -f docker/Dockerfile .

echo "=========================================================="
echo "Running tests ('$TARGET') inside isolated Docker container..."
echo "=========================================================="

docker run --rm ros-distro-ext-test bash -c "
set -e

run_wf1() {
    echo 'Running Workflow 1 Python Parsing Test...'
    .venv/bin/python3 tests/workflow_1/test_workflow_1.py
}

run_wf2() {
    echo 'Running Workflow 2 Python Parsing & Overlay Merge Test...'
    .venv/bin/python3 tests/workflow_2/test_workflow_2.py
}

run_wf3() {
    echo 'Running Workflow 3 Python Parsing & extends/dependencies Test...'
    .venv/bin/python3 tests/workflow_3/test_workflow_3.py
}

run_wf4() {
    echo 'Running Workflow 4 Python Package Name Mapping Test...'
    .venv/bin/python3 tests/workflow_4/test_workflow_4.py
}

run_wf5() {
    echo 'Running Workflow 5 Mixed Chains & Precedence Test...'
    .venv/bin/python3 tests/workflow_5/test_workflow_5.py
}

run_wf6() {
    echo 'Running Workflow 6 Chained Cache Resolution Test...'
    .venv/bin/python3 tests/workflow_6/test_workflow_6.py
}

run_wf7() {
    echo 'Running Workflow 7 Lyrical Integration Test...'
    .venv/bin/python3 tests/workflow_7/test_workflow_7.py
}

run_wf9() {
    echo 'Running Workflow 9 Lyrical & Gazebo Jetty Rebuild Test...'
    .venv/bin/python3 tests/workflow_9/test_workflow_9.py
}

run_submodules() {
    echo 'Running internal rosdistro pytest suite...'
    (cd submodules/kmom88-rosdistro && ../../.venv/bin/pytest test/)

    echo 'Running internal rosdep pytest suite...'
    (export PATH=/workspace/.venv/bin:\$PATH && cd submodules/kmom88-rosdep && ../../.venv/bin/pytest test/)

    echo 'Running internal rosinstall_generator pytest suite...'
    (cd submodules/kmom88-rosinstall_generator && ../../.venv/bin/pytest test/)

    echo 'Running internal ros_buildfarm pytest suite...'
    (cd submodules/kmom88-ros_buildfarm && ../../.venv/bin/pytest test/test_repo.py test/test_create_workspace_archive.py test/test_package_naming.py)

    echo 'Running internal superflore pytest suite...'
    (cd submodules/kmom88-superflore && ../../.venv/bin/pytest tests/test_ebuild.py)
}

run_misc() {
    echo 'Generating local Cache for Workflow 2...'
    .venv/bin/rosdistro_build_cache file:///workspace/tests/workflow_2/index.yaml rolling

    echo 'Moving generated cache files to tests/workflow_2/'
    mv rolling-cache.yaml* tests/workflow_2/

    echo 'Running rosinstall_generator turtlesim test...'
    ROSDISTRO_INDEX_URL=file:///workspace/tests/workflow_2/index.yaml .venv/bin/rosinstall_generator turtlesim --rosdistro rolling --tar

    echo 'Running rosdep database dump test...'
    ROSDISTRO_INDEX_URL=file:///workspace/tests/workflow_2/index.yaml .venv/bin/rosdep db | head -n 20
}

case \"$TARGET\" in
    1|wf1|workflow_1)
        run_wf1
        ;;
    2|wf2|workflow_2)
        run_wf2
        ;;
    3|wf3|workflow_3)
        run_wf3
        ;;
    4|wf4|workflow_4)
        run_wf4
        ;;
    5|wf5|workflow_5)
        run_wf5
        ;;
    6|wf6|workflow_6)
        run_wf6
        ;;
    7|wf7|workflow_7)
        run_wf7
        ;;
    9|wf9|workflow_9)
        run_wf9
        ;;
    submodules|pytest)
        run_submodules
        ;;
    all)
        run_wf1
        run_wf2
        run_wf3
        run_wf4
        run_wf5
        run_wf6
        run_wf7
        run_wf9
        run_submodules
        run_misc
        ;;
    *)
        if [ -f \"$TARGET\" ]; then
            echo \"Running script: $TARGET\"
            .venv/bin/python3 \"$TARGET\"
        else
            echo \"Unknown target or command: $TARGET\"
            eval \"$TARGET\"
        fi
        ;;
esac

echo \"All selected tests for '$TARGET' PASSED successfully!\"
"

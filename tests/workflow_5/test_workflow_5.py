import os
import sys
import tempfile
import shutil
import io
from urllib.request import pathname2url
import rosdistro
from rosdep2.rosdistrohelper import get_index, get_release_file
from rosdep2.gbpdistro_support import get_gbprepo_as_rosdep_data

def test_workflow_5():
    tests_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index_path = os.path.join(tests_dir, "workflow_5", "index.yaml")
    index_url = f"file://{index_path}"
    
    print(f"Loading Workflow 5 index from: {index_url}")
    os.environ['ROSDISTRO_INDEX_URL'] = index_url
    
    # 0. Setup isolated rosdep environment
    tmpdir = tempfile.mkdtemp()
    os.environ['ROS_HOME'] = tmpdir
    sources_list_dir = os.path.join(tmpdir, 'sources.list.d')
    os.makedirs(sources_list_dir)
    os.environ['ROSDEP_SOURCE_PATH'] = sources_list_dir

    dummy_yaml = os.path.join(tmpdir, 'dummy.yaml')
    with open(dummy_yaml, 'w') as y:
        y.write('')
    dummy_url = f"file://{pathname2url(dummy_yaml)}"
    with open(os.path.join(sources_list_dir, '20-default.list'), 'w') as f:
        f.write(f"yaml {dummy_url}\n")

    # Reset rosdep helper caches
    import rosdep2.rosdistrohelper
    rosdep2.rosdistrohelper._RDCache.index_url = index_url
    rosdep2.rosdistrohelper._RDCache.index = None
    rosdep2.rosdistrohelper._RDCache.release_files = {}

    from rosdep2.sources_list import update_sources_list
    update_sources_list()

    try:
        # Reset caches to force re-parsing
        rosdep2.rosdistrohelper._RDCache.release_files = {}
        
        # Redirect stdout and stderr to capture collision warnings
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = sys.stderr = mystdout = io.StringIO()
        
        try:
            # 1. Test rosdep child loading and collision logs
            print("Loading child distribution...")
            rosdep_child = get_gbprepo_as_rosdep_data('child')
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
        warnings = mystdout.getvalue()
        print("Captured Warnings:")
        print(warnings)
        
        # Assert repository and package collision warnings are printed
        assert "WARNING: Collision detected. Repository 'collision_repo' is defined in multiple parents ('parent_a' and 'parent_b'). Using definition from 'parent_a'." in warnings
        assert "WARNING: Collision detected. Package 'collision_pkg' is defined in multiple parents ('parent_a' and 'parent_b'). Using definition from 'parent_a'." in warnings

        # 2. Test DFS Precedence (parent_a takes precedence over parent_b)
        idx = rosdistro.get_index(index_url)
        child_dist = rosdistro.get_distribution_file(idx, 'child')
        
        # collision_repo version must be 1.0.0 (from parent_a), not 2.0.0 (from parent_b)
        assert child_dist.repositories['collision_repo'].release_repository.version == '1.0.0'
        
        # 3. Test Prefix Resolution for Mixed Chains in rosdep
        # std_msgs: defined in root -> A imports root via binary_import -> child imports A via binary_import.
        # Resolves to ros-root-std-msgs
        assert 'std_msgs' in rosdep_child
        ubuntu_noble_std_msgs = rosdep_child['std_msgs']['ubuntu']['noble']['apt']['packages']
        print(f"std_msgs resolves to: {ubuntu_noble_std_msgs}")
        assert ubuntu_noble_std_msgs == ['ros-root-std-msgs']

        # collision_pkg: defined in parent_a -> child imports parent_a via binary_import.
        # Resolves to ros-parent-a-collision-pkg
        assert 'collision_pkg' in rosdep_child
        ubuntu_noble_collision = rosdep_child['collision_pkg']['ubuntu']['noble']['apt']['packages']
        print(f"collision_pkg resolves to: {ubuntu_noble_collision}")
        assert ubuntu_noble_collision == ['ros-parent-a-collision-pkg']

        # child_pkg: defined in child -> resolves to ros-child-child-pkg
        assert 'child_pkg' in rosdep_child
        ubuntu_noble_child = rosdep_child['child_pkg']['ubuntu']['noble']['apt']['packages']
        print(f"child_pkg resolves to: {ubuntu_noble_child}")
        assert ubuntu_noble_child == ['ros-child-child-pkg']

    finally:
        shutil.rmtree(tmpdir)
        
    print("Workflow 5 verification test PASSED!")

if __name__ == "__main__":
    test_workflow_5()

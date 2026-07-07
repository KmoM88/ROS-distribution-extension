import os
import sys
import rosdistro
from rosdep2.rosdistrohelper import get_index, get_release_file
from rosdep2.gbpdistro_support import get_gbprepo_as_rosdep_data

def test_workflow_4():
    tests_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index_path = os.path.join(tests_dir, "workflow_4", "index.yaml")
    index_url = f"file://{index_path}"
    
    print(f"Loading Workflow 4 index from: {index_url}")
    # Force rosdistro and rosdep helper to use this index URL
    os.environ['ROSDISTRO_INDEX_URL'] = index_url
    
    # Reset rosdep helper caches
    import rosdep2.rosdistrohelper
    rosdep2.rosdistrohelper._RDCache.index_url = index_url
    rosdep2.rosdistrohelper._RDCache.index = None
    rosdep2.rosdistrohelper._RDCache.release_files = {}

    # 1. Test derived_binary (binary_import)
    print("Testing derived_binary (binary_import)...")
    rosdep_binary = get_gbprepo_as_rosdep_data('derived_binary')
    
    # Assert turtlesim (imported from base via binary_import) resolves to ros-base-turtlesim
    assert 'turtlesim' in rosdep_binary
    ubuntu_noble_turtlesim = rosdep_binary['turtlesim']['ubuntu']['noble']['apt']['packages']
    print(f"turtlesim resolves to: {ubuntu_noble_turtlesim}")
    assert ubuntu_noble_turtlesim == ['ros-base-turtlesim']
    
    # Assert new_package (defined in derived_binary) resolves to ros-derived-binary-new-package
    assert 'new_package' in rosdep_binary
    ubuntu_noble_new_pkg = rosdep_binary['new_package']['ubuntu']['noble']['apt']['packages']
    print(f"new_package resolves to: {ubuntu_noble_new_pkg}")
    assert ubuntu_noble_new_pkg == ['ros-derived-binary-new-package']
    
    # 2. Test derived_source (source_rebuild)
    print("Testing derived_source (source_rebuild)...")
    rosdep_source = get_gbprepo_as_rosdep_data('derived_source')
    
    # Assert turtlesim (rebuilt in derived_source) resolves to ros-derived-source-turtlesim
    assert 'turtlesim' in rosdep_source
    ubuntu_noble_turtlesim_src = rosdep_source['turtlesim']['ubuntu']['noble']['apt']['packages']
    print(f"turtlesim resolves to: {ubuntu_noble_turtlesim_src}")
    assert ubuntu_noble_turtlesim_src == ['ros-derived-source-turtlesim']
    
    print("Workflow 4 verification test PASSED!")

if __name__ == "__main__":
    test_workflow_4()

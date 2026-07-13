import os
import sys
from io import StringIO
import rosdistro
from rosdistro import CircularInheritanceError

def test_workflow_3():
    tests_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index_path = os.path.join(tests_dir, "workflow_3", "index.yaml")
    index_url = f"file://{index_path}"
    
    print(f"Loading Workflow 3 index from: {index_url}")
    index = rosdistro.get_index(index_url)
    
    # 1. Capture stdout and stderr to check for platform compatibility warning
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = sys.stderr = mystdout = StringIO()
    
    try:
        dist_file = rosdistro.get_distribution_file(index, 'derived')
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        
    print("Verification output from stdout:")
    print(mystdout.getvalue())
    
    # Assert platform warning was printed
    warning_msg = "WARNING: Target platform 'ubuntu:oracular' specified in derived distribution is not supported by base distribution."
    assert warning_msg in mystdout.getvalue()
    
    # Assert merged repositories
    assert 'ros_tutorials' in dist_file.repositories
    assert 'new_derived_repo' in dist_file.repositories
    
    # Assert extends block parsed
    assert len(dist_file.extends) == 1
    assert dist_file.extends[0]['distro_name'] == 'base'
    assert dist_file.extends[0]['extension_method'] == 'binary_import'
    
    # Assert dependencies block parsed
    assert len(dist_file.dependencies) == 1
    assert dist_file.dependencies[0]['rosdep_sources_list_urls'] == [
        'https://raw.githubusercontent.com/ros/rosdistro/master/rosdep/base.yaml'
    ]
    assert dist_file.dependencies[0]['rosdep_minimum_target_platforms'] == [
        'ubuntu:noble',
        'debian:bookworm'
    ]
    
    # 2. Test Circular Inheritance loop detection
    print("Testing circular inheritance loop detection...")
    try:
        rosdistro.get_distribution_file(index, 'cyclic')
        assert False, "Expected CircularInheritanceError was not raised!"
    except CircularInheritanceError as e:
        print(f"Circular inheritance caught successfully: {e}")
        assert "Circular inheritance detected" in str(e)
        
    print("Workflow 3 verification test PASSED!")

if __name__ == "__main__":
    test_workflow_3()

import os
import rosdistro

def test_workflow_1():
    tests_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index_path = os.path.join(tests_dir, "workflow_1", "index.yaml")
    index_url = f"file://{index_path}"
    
    print(f"Loading Workflow 1 index from: {index_url}")
    index = rosdistro.get_index(index_url)
    
    assert index.version == 3
    assert 'rolling' in index.distributions
    
    dist_file = rosdistro.get_distribution_file(index, 'rolling')
    assert 'ros_tutorials' in dist_file.repositories
    assert 'turtlesim' in dist_file.repositories['ros_tutorials'].release_repository.package_names
    print("Workflow 1 verification test PASSED!")

if __name__ == "__main__":
    test_workflow_1()

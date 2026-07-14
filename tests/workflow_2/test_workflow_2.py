import os
import rosdistro

def test_workflow_2():
    tests_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index_path = os.path.join(tests_dir, "workflow_2", "index.yaml")
    index_url = f"file://{index_path}"
    
    print("#"*60)
    print(f"Loading Workflow 2 index from: {index_url}")
    print("#"*60)
    index = rosdistro.get_index(index_url)
    
    assert index.version == 3
    assert 'rolling' in index.distributions
    
    dist_info = index.distributions['rolling']
    assert len(dist_info['distribution']) == 2
    
    print("Testing get_distribution_file merging behavior...")
    dist_file = rosdistro.get_distribution_file(index, 'rolling')
    
    # Assert merged repositories
    assert 'ros_tutorials' in dist_file.repositories
    assert 'new_repo' in dist_file.repositories
    
    # Assert overlay override (status: developed)
    ros_tutorials_repo = dist_file.repositories['ros_tutorials']
    assert ros_tutorials_repo.status == 'developed'
    
    # Assert base package remains intact
    assert 'turtlesim' in ros_tutorials_repo.release_repository.package_names
    
    print("Workflow 2 verification test PASSED!")

if __name__ == "__main__":
    test_workflow_2()

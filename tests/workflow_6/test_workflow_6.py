#!/usr/bin/env python3
import os
import shutil
import subprocess
import yaml
import rosdistro

def test_workflow_6():
    tests_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    workflow_dir = os.path.join(tests_dir, "workflow_6")
    index_path = os.path.join(workflow_dir, "index.yaml")
    index_url = f"file://{index_path}"
    
    print(f"Loading Workflow 6 index from: {index_url}")
    
    # 1. Clean existing cache files
    for name in ['base-cache.yaml', 'base-cache.yaml.gz', 'derived-cache.yaml', 'derived-cache.yaml.gz']:
        path = os.path.join(workflow_dir, name)
        if os.path.exists(path):
            os.remove(path)
            
    # 2. Run rosdistro_build_cache for both distributions
    print("Building cache for 'base'...")
    subprocess.check_call([
        '.venv/bin/rosdistro_build_cache',
        index_url,
        'base'
    ])
    
    print("Building cache for 'derived'...")
    subprocess.check_call([
        '.venv/bin/rosdistro_build_cache',
        index_url,
        'derived'
    ])
    
    # Move generated caches to workflow_dir
    for name in ['base-cache.yaml', 'base-cache.yaml.gz', 'derived-cache.yaml', 'derived-cache.yaml.gz']:
        if os.path.exists(name):
            shutil.move(name, os.path.join(workflow_dir, name))
            
    # 3. Verify minimal cache files on disk
    with open(os.path.join(workflow_dir, 'base-cache.yaml'), 'r') as f:
        base_cache_data = yaml.safe_load(f)
    with open(os.path.join(workflow_dir, 'derived-cache.yaml'), 'r') as f:
        derived_cache_data = yaml.safe_load(f)
        
    print("Verifying base cache...")
    assert 'turtlesim' in base_cache_data['release_package_xmls']
    assert 'roscpp_tutorials' not in base_cache_data['release_package_xmls']
    
    print("Verifying derived cache (should be minimal)...")
    assert 'roscpp_tutorials' in derived_cache_data['release_package_xmls']
    assert 'turtlesim' not in derived_cache_data['release_package_xmls'] # Minimal check
    
    # 4. Verify memory loading and chained resolution
    idx = rosdistro.get_index(index_url)
    
    print("Loading cached distribution for 'derived' (with chaining)...")
    dist = rosdistro.get_cached_distribution(idx, 'derived')
    
    # Should resolve both thanks to chained cache loading
    assert 'roscpp_tutorials' in dist.release_packages
    assert 'turtlesim' in dist.release_packages
    
    # Should successfully load package XMLs for both
    assert dist.get_release_package_xml('roscpp_tutorials') is not None
    assert dist.get_release_package_xml('turtlesim') is not None
    
    # 5. Run rosinstall_generator turtlesim roscpp_tutorials to verify consumer integration
    print("Testing rosinstall_generator dependency resolution with chained caches...")
    env = os.environ.copy()
    env['ROSDISTRO_INDEX_URL'] = index_url
    
    output = subprocess.check_output([
        '.venv/bin/rosinstall_generator',
        'roscpp_tutorials', 'turtlesim',
        '--rosdistro', 'derived',
        '--tar'
    ], env=env).decode('utf-8')
    
    print("Rosinstall generator output:")
    print(output)
    
    # Verify both packages are in the generated rosinstall output
    assert 'local-name: roscpp_tutorials' in output
    assert 'local-name: turtlesim' in output
    
    print("Workflow 6 verification test PASSED!")

if __name__ == '__main__':
    test_workflow_6()

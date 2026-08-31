#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import yaml
import rosdistro

def test_workflow_9():
    workflow_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(workflow_dir, "index.yaml")
    index_url = f"file://{index_path}"
    
    print("#"*60)
    print(f"Loading Workflow 9 index from: {index_url}")
    print("#"*60)
    os.environ['ROSDISTRO_INDEX_URL'] = index_url

    idx = rosdistro.get_index(index_url)

    # 1. Verify in-memory distribution file extends resolution
    print("Loading distribution file for 'lyrical' from submodule...")
    dist_file = rosdistro.get_distribution_file(idx, 'lyrical')
    
    # Verify packages defined in submodules/ros-rosdistro/lyrical/distribution.yaml
    assert 'std_msgs' in dist_file.release_packages
    assert 'turtlesim' in dist_file.release_packages
    
    # Verify Gazebo Jetty packages inherited via source_rebuild from submodules/gazebodistro
    assert 'gz-sim' in dist_file.repositories
    assert 'gz-transport' in dist_file.repositories
    assert 'sdformat' in dist_file.repositories
    
    # Verify git source repository metadata is correctly inherited
    gz_sim_repo = dist_file.repositories['gz-sim']
    assert gz_sim_repo.source_repository is not None
    assert gz_sim_repo.source_repository.type == 'git'
    assert gz_sim_repo.source_repository.url == 'https://github.com/gazebosim/gz-sim'
    assert gz_sim_repo.source_repository.version == 'gz-sim10'
    print("Inherited Gazebo source repository 'gz-sim' verified successfully.")

    # 2. Verify in-memory chained cache resolution
    print("Loading cached distribution for 'lyrical' (testing chained in-memory cache)...")
    cached_dist = rosdistro.get_cached_distribution(idx, 'lyrical')
    
    # Local packages in lyrical cache
    assert 'std_msgs' in cached_dist.release_packages
    assert 'turtlesim' in cached_dist.release_packages
    
    # Chained packages from jetty cache
    assert 'gz-sim' in cached_dist.release_packages
    assert 'gz-cmake' in cached_dist.release_packages
    assert 'gz-common' in cached_dist.release_packages
    print("In-memory chained cache packages verified successfully.")

    # 3. Verify rosinstall_generator resolutions across chained boundaries
    print("Testing rosinstall_generator repository resolution for inherited Gazebo package...")
    env = os.environ.copy()
    env['ROSDISTRO_INDEX_URL'] = index_url
    
    output = subprocess.check_output([
        '.venv/bin/rosinstall_generator',
        'gz-sim',
        '--rosdistro', 'lyrical',
        '--upstream'
    ], env=env).decode('utf-8')
    
    print("Rosinstall generator output:")
    print(output)
    assert 'local-name: gz-sim' in output
    assert 'uri: https://github.com/gazebosim/gz-sim' in output

    # 4. Verify rosdep resolution under source_rebuild
    print("Testing rosdep package resolutions under source_rebuild...")
    import tempfile
    from urllib.request import pathname2url
    import rosdep2.rosdistrohelper
    from rosdep2.gbpdistro_support import get_gbprepo_as_rosdep_data

    tmpdir = tempfile.mkdtemp()
    try:
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
        rosdep2.rosdistrohelper._RDCache.index_url = index_url
        rosdep2.rosdistrohelper._RDCache.index = None
        rosdep2.rosdistrohelper._RDCache.release_files = {}

        from rosdep2.sources_list import update_sources_list
        update_sources_list()

        rosdep_lyrical = get_gbprepo_as_rosdep_data('lyrical')
        
        # Verify packages in lyrical resolve with ros-lyrical- prefix
        assert 'std_msgs' in rosdep_lyrical
        assert 'turtlesim' in rosdep_lyrical
        assert 'ros_gz_sim' in rosdep_lyrical
        assert 'ros_gz_bridge' in rosdep_lyrical

        res_turtlesim = rosdep_lyrical['turtlesim']['ubuntu']['resolute']['apt']['packages']
        print(f"lyrical turtlesim resolves to: {res_turtlesim}")
        assert res_turtlesim == ['ros-lyrical-turtlesim']

        res_std_msgs = rosdep_lyrical['std_msgs']['ubuntu']['resolute']['apt']['packages']
        print(f"lyrical std_msgs resolves to: {res_std_msgs}")
        assert res_std_msgs == ['ros-lyrical-std-msgs']

        res_ros_gz_sim = rosdep_lyrical['ros_gz_sim']['ubuntu']['resolute']['apt']['packages']
        print(f"lyrical ros_gz_sim resolves to: {res_ros_gz_sim}")
        assert res_ros_gz_sim == ['ros-lyrical-ros-gz-sim']

        res_ros_gz_bridge = rosdep_lyrical['ros_gz_bridge']['ubuntu']['resolute']['apt']['packages']
        print(f"lyrical ros_gz_bridge resolves to: {res_ros_gz_bridge}")
        assert res_ros_gz_bridge == ['ros-lyrical-ros-gz-bridge']

        print("rosdep package resolutions for all targeted packages verified successfully.")
    finally:
        shutil.rmtree(tmpdir)

    print("Workflow 9 verification test PASSED!")

if __name__ == "__main__":
    test_workflow_9()

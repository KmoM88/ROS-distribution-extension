#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import tempfile
import yaml
import rosdistro
from urllib.request import pathname2url
from rosdep2.rosdistrohelper import get_index, get_release_file
from rosdep2.gbpdistro_support import get_gbprepo_as_rosdep_data
from bloom.generators.common import resolve_rosdep_key
from superflore.generators.ebuild.ebuild import Ebuild
from superflore.generators.ebuild.gen_packages import _gen_ebuild_for_package
from unittest.mock import MagicMock

def test_workflow_7():
    workflow_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(workflow_dir, "index.yaml")
    index_url = f"file://{index_path}"
    
    print("#"*60)
    print(f"Loading Workflow 7 index from: {index_url}")
    print("#"*60)
    os.environ['ROSDISTRO_INDEX_URL'] = index_url
    
    # 1. Clean existing cache files
    cache_names = [
        'lyrical-cache.yaml', 'lyrical-cache.yaml.gz',
        'parent_gazebo-cache.yaml', 'parent_gazebo-cache.yaml.gz',
        'derived_binary-cache.yaml', 'derived_binary-cache.yaml.gz',
        'derived_source-cache.yaml', 'derived_source-cache.yaml.gz'
    ]
    for name in cache_names:
        path = os.path.join(workflow_dir, name)
        if os.path.exists(path):
            os.remove(path)
            
    # 2. Run rosdistro_build_cache to build caches on disk
    distro_names = ['lyrical', 'parent_gazebo', 'derived_binary', 'derived_source']
    for distro in distro_names:
        print(f"Building cache for '{distro}'...")
        subprocess.check_call([
            '.venv/bin/rosdistro_build_cache',
            index_url,
            distro
        ])
        # Move generated cache files from root directory to workflow_dir
        for ext in ['-cache.yaml', '-cache.yaml.gz']:
            gen_name = f"{distro}{ext}"
            if os.path.exists(gen_name):
                shutil.move(gen_name, os.path.join(workflow_dir, gen_name))

    # 3. Assert minimal cache files on disk
    with open(os.path.join(workflow_dir, 'derived_binary-cache.yaml'), 'r') as f:
        derived_binary_cache = yaml.safe_load(f)
    with open(os.path.join(workflow_dir, 'derived_source-cache.yaml'), 'r') as f:
        derived_source_cache = yaml.safe_load(f)

    print("Verifying derived_binary cache is minimal...")
    assert 'roscpp_tutorials' in derived_binary_cache['release_package_xmls']
    assert 'gazebo_ros_pkgs' not in derived_binary_cache['release_package_xmls']
    assert 'turtlesim' not in derived_binary_cache['release_package_xmls']

    print("Verifying derived_source cache is minimal...")
    assert 'turtlesim' in derived_source_cache['release_package_xmls']
    assert 'gazebo_ros_pkgs' not in derived_source_cache['release_package_xmls']
    assert 'std_msgs' not in derived_source_cache['release_package_xmls']

    # 4. Verify in-memory chained cache resolution
    idx = rosdistro.get_index(index_url)
    print("Loading cached distribution for 'derived_binary' (verifying chaining)...")
    dist = rosdistro.get_cached_distribution(idx, 'derived_binary')
    
    assert 'roscpp_tutorials' in dist.release_packages
    assert 'gazebo_ros_pkgs' in dist.release_packages
    assert 'turtlesim' in dist.release_packages
    assert 'std_msgs' in dist.release_packages

    # 5. Setup isolated rosdep environment
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
        # 6. Test rosdep resolutions
        print("Testing rosdep package resolutions...")
        rosdep_binary = get_gbprepo_as_rosdep_data('derived_binary')
        
        # Binary Import: turtlesim from lyrical remains ros-lyrical-turtlesim
        assert 'turtlesim' in rosdep_binary
        res_turtlesim = rosdep_binary['turtlesim']['ubuntu']['Resolutes']['apt']['packages']
        print(f"derived_binary turtlesim resolves to: {res_turtlesim}")
        assert res_turtlesim == ['ros-lyrical-turtlesim']

        # Binary Import: gazebo_ros_pkgs remains ros-parent-gazebo-gazebo-ros-pkgs
        assert 'gazebo_ros_pkgs' in rosdep_binary
        res_gazebo = rosdep_binary['gazebo_ros_pkgs']['ubuntu']['Resolutes']['apt']['packages']
        print(f"derived_binary gazebo_ros_pkgs resolves to: {res_gazebo}")
        assert res_gazebo == ['ros-parent-gazebo-gazebo-ros-pkgs']

        # Source Rebuild resolutions
        rosdep_source = get_gbprepo_as_rosdep_data('derived_source')
        
        # Source Rebuild: turtlesim overrides base and maps to ros-derived-source-turtlesim
        assert 'turtlesim' in rosdep_source
        res_turtlesim_src = rosdep_source['turtlesim']['ubuntu']['Resolutes']['apt']['packages']
        print(f"derived_source turtlesim resolves to: {res_turtlesim_src}")
        assert res_turtlesim_src == ['ros-derived-source-turtlesim']

        # Source Rebuild: std_msgs maps to ros-derived-source-std-msgs
        assert 'std_msgs' in rosdep_source
        res_std_msgs_src = rosdep_source['std_msgs']['ubuntu']['Resolutes']['apt']['packages']
        print(f"derived_source std_msgs resolves to: {res_std_msgs_src}")
        assert res_std_msgs_src == ['ros-derived-source-std-msgs']

        # 7. Verify bloom RosDebianGenerator resolution
        print("Testing bloom RosDebianGenerator resolution...")
        resolved, _, _ = resolve_rosdep_key('turtlesim', 'ubuntu', 'Resolutes', 'derived_binary')
        print(f"bloom resolved turtlesim to: {resolved}")
        assert resolved == ['ros-lyrical-turtlesim']

        # 8. Verify superflore category mappings
        print("Testing superflore ebuild generation...")
        distro_file = rosdistro.get_distribution_file(idx, 'derived_binary')
        ros_pkg = MagicMock()
        ros_pkg.get_package_xml.return_value = """<package format="3">
  <name>test_pkg</name>
  <version>1.0.0</version>
  <description>Test package</description>
  <maintainer email="test@test.com">test</maintainer>
  <license>BSD</license>
  <depend>turtlesim</depend>
  <depend>gazebo_ros_pkgs</depend>
</package>"""
        class MockDepWalker:
            def __init__(self, *args, **kwargs): pass
            def get_depends(self, pkg_name, dep_type):
                return ["turtlesim", "gazebo_ros_pkgs"] if dep_type == "run" else []

        import superflore.generators.ebuild.gen_packages
        original_walker = superflore.generators.ebuild.gen_packages.DependencyWalker
        superflore.generators.ebuild.gen_packages.DependencyWalker = MockDepWalker
        
        try:
            original_get_package_names = superflore.generators.ebuild.gen_packages.get_package_names
            superflore.generators.ebuild.gen_packages.get_package_names = lambda distro: (["turtlesim", "gazebo_ros_pkgs"], [])
            
            pkg = MagicMock()
            pkg.upstream_license = ["BSD"]
            pkg.description = "Test package"
            pkg.homepage = "https://wiki.ros.org"
            pkg.build_type = "catkin"
            pkg.upstream_email = "test@test.com"
            pkg.upstream_name = "test_pkg"
            pkg.longdescription = "long description"
            repo = MagicMock()
            repo.url = "https://github.com/ros-gbp/test_pkg-release.git"
            pkg_rosinstall = [{'tar': {'uri': 'https://github.com/ros-gbp/test_pkg-release/archive/1.0.0.tar.gz'}}]
            
            ebuild_obj = _gen_ebuild_for_package(
                distro_file, "test_pkg", pkg, repo, ros_pkg, pkg_rosinstall
            )
            ebuild_obj.name = "test_pkg"
            
            print(f"superflore ebuild rdepends: {ebuild_obj.rdepends}")
            assert ebuild_obj.rdepends["turtlesim"] == "lyrical"
            assert ebuild_obj.rdepends["gazebo_ros_pkgs"] == "parent_gazebo"
            
            ebuild_text = ebuild_obj.get_ebuild_text("Open Source Robotics Foundation", "BSD")
            print(f"Generated ebuild text:\n{ebuild_text}")
            assert "ros-lyrical/turtlesim" in ebuild_text
            assert "ros-parent_gazebo/gazebo_ros_pkgs" in ebuild_text
        finally:
            superflore.generators.ebuild.gen_packages.DependencyWalker = original_walker
            superflore.generators.ebuild.gen_packages.get_package_names = original_get_package_names

        # 9. Verify rosinstall_generator resolutions across chained boundaries
        print("Testing rosinstall_generator dependency resolution with chained caches...")
        env = os.environ.copy()
        env['ROSDISTRO_INDEX_URL'] = index_url
        
        output = subprocess.check_output([
            '.venv/bin/rosinstall_generator',
            'roscpp_tutorials', 'gazebo_ros_pkgs', 'turtlesim',
            '--rosdistro', 'derived_binary',
            '--tar'
        ], env=env).decode('utf-8')
        
        print("Rosinstall generator output:")
        print(output)
        assert 'local-name: roscpp_tutorials' in output
        assert 'local-name: gazebo_ros_pkgs' in output
        assert 'local-name: turtlesim' in output

        # 10. Verify ros_buildfarm package name prefix resolutions
        print("Testing ros_buildfarm naming prefix resolution...")
        from ros_buildfarm.common import get_os_package_name
        pkg_name = get_os_package_name('derived_binary', 'turtlesim', distro_file)
        print(f"ros_buildfarm package name: {pkg_name}")
        assert pkg_name == 'ros-lyrical-turtlesim'

    finally:
        shutil.rmtree(tmpdir)
        
    print("Workflow 7 verification test PASSED!")

if __name__ == "__main__":
    test_workflow_7()

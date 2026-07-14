import os
import sys
import tempfile
import shutil
from urllib.request import pathname2url
import rosdistro
from rosdep2.rosdistrohelper import get_index, get_release_file
from rosdep2.gbpdistro_support import get_gbprepo_as_rosdep_data

def test_workflow_4():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(script_dir, "index.yaml")
    index_url = f"file://{index_path}"
    
    print("#"*60)
    print(f"Loading Workflow 4 index from: {index_url}")
    print("#"*60)

    # Force rosdistro and rosdep helper to use this index URL
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
        # 1. Test rosdep derived_binary (binary_import)
        print("Testing rosdep derived_binary (binary_import)...")
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
        
        # 2. Test rosdep derived_source (source_rebuild)
        print("Testing rosdep derived_source (source_rebuild)...")
        rosdep_source = get_gbprepo_as_rosdep_data('derived_source')
        
        # Assert turtlesim (rebuilt in derived_source) resolves to ros-derived-source-turtlesim
        assert 'turtlesim' in rosdep_source
        ubuntu_noble_turtlesim_src = rosdep_source['turtlesim']['ubuntu']['noble']['apt']['packages']
        print(f"turtlesim resolves to: {ubuntu_noble_turtlesim_src}")
        assert ubuntu_noble_turtlesim_src == ['ros-derived-source-turtlesim']

        # 3. Test bloom RosDebianGenerator on derived_binary
        print("Testing bloom RosDebianGenerator...")
        from bloom.generators.rosdebian import RosDebianGenerator
        from bloom.generators.common import resolve_rosdep_key
        
        # Verify resolve_rosdep_key in this context
        # Since bloom uses rosdep under the hood (which is already configured with the mock index_url),
        # calling bloom's resolve_rosdep_key should resolve turtlesim to ['ros-base-turtlesim']
        resolved, _, _ = resolve_rosdep_key('turtlesim', 'ubuntu', 'noble', 'derived_binary')
        print(f"bloom resolved turtlesim to: {resolved}")
        assert resolved == ['ros-base-turtlesim']
        
        resolved_new, _, _ = resolve_rosdep_key('new_package', 'ubuntu', 'noble', 'derived_binary')
        print(f"bloom resolved new_package to: {resolved_new}")
        assert resolved_new == ['ros-derived-binary-new-package']

        # 4. Test superflore ebuild generation on derived_binary
        print("Testing superflore ebuild generation...")
        from superflore.generators.ebuild.ebuild import Ebuild
        from superflore.generators.ebuild.gen_packages import _gen_ebuild_for_package
        from unittest.mock import MagicMock
        
        # Let's load the index and distribution file
        idx = rosdistro.get_index(index_url)
        distro_file = rosdistro.get_distribution_file(idx, 'derived_binary')
        
        # Mock a package metadata object
        ros_pkg = MagicMock()
        ros_pkg.get_package_xml.return_value = """<package format="3">
  <name>test_pkg</name>
  <version>1.0.0</version>
  <description>Test package</description>
  <maintainer email="test@test.com">test</maintainer>
  <license>BSD</license>
  <depend>turtlesim</depend>
  <depend>new_package</depend>
</package>"""
        class MockDepWalker:
            def __init__(self, *args, **kwargs):
                pass
            def get_depends(self, pkg_name, dep_type):
                if dep_type == "run":
                    return ["turtlesim", "new_package"]
                return []
                
        # Mock DependencyWalker class in gen_packages.py
        import superflore.generators.ebuild.gen_packages
        original_walker = superflore.generators.ebuild.gen_packages.DependencyWalker
        superflore.generators.ebuild.gen_packages.DependencyWalker = MockDepWalker
        
        try:
            # Mock get_package_names
            original_get_package_names = superflore.generators.ebuild.gen_packages.get_package_names
            superflore.generators.ebuild.gen_packages.get_package_names = lambda distro: ([
                "turtlesim", "new_package"
            ], [])
            
            # Call _gen_ebuild_for_package
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
            
            # Verify ebuild_obj's rdepends keys and distro values
            print(f"superflore ebuild rdepends: {ebuild_obj.rdepends}")
            assert ebuild_obj.rdepends["turtlesim"] == "base"
            assert ebuild_obj.rdepends["new_package"] == "derived_binary"
            
            # Get generated ebuild text and assert categories are correct
            ebuild_text = ebuild_obj.get_ebuild_text("Open Source Robotics Foundation", "BSD")
            print(f"Generated ebuild text:\n{ebuild_text}")
            assert "ros-base/turtlesim" in ebuild_text
            assert "ros-derived_binary/new_package" in ebuild_text
            
        finally:
            # Restore original classes
            superflore.generators.ebuild.gen_packages.DependencyWalker = original_walker
            superflore.generators.ebuild.gen_packages.get_package_names = original_get_package_names

    finally:
        shutil.rmtree(tmpdir)
    
    print("Workflow 4 verification test PASSED!")

if __name__ == "__main__":
    test_workflow_4()

import pecan_mount
from pytest import raises


class TestTreeMount(object):

    def setup(self):
        pecan_mount.tree.apps = {}
        self.conf = {
            'app': {
            'root': 'pecan_mount.tests.app.basic.RootController',
            'modules': ['pecan_mount.tests.app']
            }
        }

    def test_empty_mount_locations(self):
        assert pecan_mount.tree.apps == {}

    def test_add_app_to_tree(self):
        pecan_mount.tree.mount(None, '', self.conf)
        assert pecan_mount.tree.apps[''] is not None

    def test_add_app_to_tree_has_script_name(self):
        pecan_mount.tree.mount(None, '', self.conf)
        assert pecan_mount.tree.apps[''].script_name == ''

    def test_fail_to_add_two_apps_in_same_location(self):
        pecan_mount.tree.mount(None, '', self.conf)
        with raises(AttributeError) as exc:
            pecan_mount.tree.mount(None, '', self.conf)
        assert "script_name <''" in exc.value[0]
        assert 'is already mounted' in exc.value[0]

    def test_strip_trailing_slash(self):
        pecan_mount.tree.mount(None, '/foo/', self.conf)
        assert pecan_mount.tree.apps['/foo']
        assert pecan_mount.tree.apps.get('/foo/') is None


class TestTreeScriptName(object):

    def setup(self):
        pecan_mount.tree.apps = {}
        self.conf = {
            'app': {
            'root': 'pecan_mount.tests.app.basic.RootController',
            'modules': ['pecan_mount.tests.app']
            }
        }

    def test_return_none(self):
        assert pecan_mount.tree.script_name('/') is None

    def test_return_path(self):
        pecan_mount.tree.mount(None, '/foo', self.conf)
        assert pecan_mount.tree.script_name('/foo') == '/foo'

    def test_return_nested_path(self):
        pecan_mount.tree.mount(None, '/foo', self.conf)
        assert pecan_mount.tree.script_name('/foo/bar/baz') == '/foo'

    def test_return_none_if_path_is_empty(self):
        # if is emtpy and is not in self.apps
        pecan_mount.tree.mount(None, '/foo', self.conf)
        assert pecan_mount.tree.script_name('') == None

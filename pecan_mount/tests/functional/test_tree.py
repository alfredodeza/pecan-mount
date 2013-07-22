from webtest import TestApp as WebTestApp
import pecan_mount


class TestTwoApps(object):

    def setup(self):
        pecan_mount.tree.apps = {}
        self.conf = {
            'app': {
            'root': 'pecan_mount.tests.app.basic.RootController',
            'modules': ['pecan_mount.tests.app']
            }
        }

    def test_not_found_if_root_is_empty(self):
        pecan_mount.tree.mount('/foo', self.conf)
        pecan_mount.tree.mount('/bar', self.conf)
        app = WebTestApp(pecan_mount.tree)
        result =  app.get('/', expect_errors=True)
        assert result.status_int == 404

    def test_run_two_apps(self):
        pecan_mount.tree.mount('/foo', self.conf)
        pecan_mount.tree.mount('/bar', self.conf)
        app = WebTestApp(pecan_mount.tree)
        assert app.get('/bar/')
        assert app.get('/foo/')

    def test_run_two_nested_apps(self):
        pecan_mount.tree.mount('/foo/baz', self.conf)
        pecan_mount.tree.mount('/bar/foo/foo', self.conf)
        app = WebTestApp(pecan_mount.tree)
        assert app.get('/bar/foo/foo')
        assert  app.get('/foo/baz')


from pecan_mount import _tree as tree


class TestNameFromPath(object):

    def test_empty_string_is_root(self):
        assert tree.name_from_path('') == 'root'

    def test_empty_or_none_is_root(self):
        assert tree.name_from_path(None) == 'root'

    def test_last_part_from_url_is_name(self):
        assert tree.name_from_path('/foo') == 'foo'

    def test_get_dotted_name_from_nested_paths(self):
        assert tree.name_from_path('/foo/bar/baz') == 'foo.bar.baz'

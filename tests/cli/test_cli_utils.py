from tagkit.cli.cli_utils import tag_ids_to_int


class TestTagIdsToInt:
    def test_with_none(self):
        assert tag_ids_to_int(None) is None

    def test_with_ints(self):
        assert tag_ids_to_int("1,2,3") == [1, 2, 3]

    def test_with_mix(self):
        assert tag_ids_to_int("1,a,2") == [1, "a", 2]

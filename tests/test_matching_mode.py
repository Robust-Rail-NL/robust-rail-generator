"""`matching` is FIFO, random or LIFO; the integers 0, 1 and 2 are accepted for one more release, with a warning."""

import logging

import pytest

from matching_mode import matching_name, normalize_matching_setting


class TestMatchingName:
    @pytest.mark.parametrize("name", ["FIFO", "random", "LIFO"])
    def test_a_name_is_kept(self, name):
        assert matching_name(name) == name

    @pytest.mark.parametrize("legacy, name", [(0, "FIFO"), (1, "random"), (2, "LIFO")])
    def test_a_legacy_integer_maps_to_its_name(self, legacy, name):
        assert matching_name(legacy) == name

    @pytest.mark.parametrize("value", [3, -1, True, False, 1.0, "fifo", "reverse", None, [0]])
    def test_anything_else_is_refused(self, value):
        with pytest.raises(ValueError):
            matching_name(value)


class TestNormalizeMatchingSetting:
    def test_absent_means_random(self):
        config = {}
        assert normalize_matching_setting(config)
        assert config["matching"] == "random"

    def test_a_name_passes_without_a_warning(self, caplog):
        config = {"matching": "LIFO"}
        with caplog.at_level(logging.WARNING):
            assert normalize_matching_setting(config)
        assert config["matching"] == "LIFO"
        assert caplog.records == []

    @pytest.mark.parametrize("legacy, name", [(0, "FIFO"), (1, "random"), (2, "LIFO")])
    def test_a_legacy_integer_is_converted_with_a_deprecation_warning(self, legacy, name, caplog):
        config = {"matching": legacy}
        with caplog.at_level(logging.WARNING):
            assert normalize_matching_setting(config)
        assert config["matching"] == name
        assert any("deprecated" in r.message and name in r.message for r in caplog.records)

    def test_an_invalid_value_is_an_error(self, caplog):
        config = {"matching": 7}
        with caplog.at_level(logging.ERROR):
            assert not normalize_matching_setting(config)
        assert any("'matching' should be one of" in r.message for r in caplog.records)

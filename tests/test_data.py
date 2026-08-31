import json
import os
import re

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


class TestDefaultTrainUnitTypesData:
    """Regression guard for the 'SGMm' typePrefix typo found while
    implementing the type_prefix/carriages rename: a lowercase letter in a
    typePrefix silently breaks the (typePrefix, carriages) identity match
    against config files that reference the correct family name."""

    def test_type_prefixes_are_uppercase(self):
        with open(f"{DATA_DIR}/default_train_unit_types.json") as f:
            data = json.load(f)
        for entry in data:
            assert re.fullmatch(r"[A-Z]+", entry["typePrefix"]), (
                f"typePrefix {entry['typePrefix']!r} for {entry['name']!r} is not all-uppercase"
            )

"""Tests for the typePrefix/carriages identity rename and TaskSpec.optional
(Phase 2 of the 2.0.0 roadmap, see unified-schema-design.md)."""

import json
import re

import pytest

from models.scenario import IncomingTrainUnit, TaskSpec, TrainUnit, TrainUnitType

DATA_DIR = __import__("os").path.join(
    __import__("os").path.dirname(__file__), "..", "data"
)


class TestTrainUnitType:
    def test_identity_is_type_prefix_and_carriages(self):
        a = TrainUnitType(type_prefix="SLT", carriages=4)
        b = TrainUnitType(type_prefix="SLT", carriages=4)
        c = TrainUnitType(type_prefix="SLT", carriages=6)
        assert a == b
        assert hash(a) == hash(b)
        assert a != c

    def test_type_display_name_is_derived_not_a_wire_field(self):
        t = TrainUnitType(type_prefix="SLT", carriages=4)
        assert t.type_display_name == "SLT-4"
        assert "typeDisplayName" not in t.to_dict()

    def test_wire_shape_uses_type_prefix(self):
        t = TrainUnitType.model_validate({"typePrefix": "VIRM", "carriages": 6})
        assert t.type_prefix == "VIRM"
        assert t.to_dict()["typePrefix"] == "VIRM"
        assert "displayName" not in t.to_dict()

    def test_display_name_rejected_as_extra_field(self):
        with pytest.raises(Exception):
            TrainUnitType.model_validate({"displayName": "SLT", "carriages": 4})


class TestTrainUnit:
    def test_type_prefix_and_carriages_are_required(self):
        u = TrainUnit(type_prefix="SLT", carriages=4)
        assert u.type_display_name == "SLT-4"
        assert u.to_dict()["typePrefix"] == "SLT"
        assert u.to_dict()["carriages"] == 4

    def test_incoming_train_unit_from_train_unit_copies_type_fields(self):
        base = TrainUnit(type_prefix="VIRM", carriages=6, id="2401")
        incoming = IncomingTrainUnit.from_train_unit(base)
        assert incoming.type_prefix == "VIRM"
        assert incoming.carriages == 6
        assert incoming.id == "2401"


class TestTaskSpec:
    def test_optional_defaults_false(self):
        spec = TaskSpec()
        assert spec.optional is False

    def test_optional_omitted_from_wire_when_unset(self):
        spec = TaskSpec(duration=60)
        assert "optional" not in spec.to_dict()

    def test_optional_present_when_explicitly_set(self):
        spec = TaskSpec(duration=60, optional=True)
        assert spec.to_dict()["optional"] is True


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
                f"typePrefix {entry['typePrefix']!r} for {entry['name']!r} "
                "is not all-uppercase"
            )

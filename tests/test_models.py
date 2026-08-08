"""Tests for the typePrefix/carriages identity rename and TaskSpec.optional
(Phase 2 of the 2.0.0 roadmap, see unified-schema-design.md)."""

import json
import re

import pytest

from pydantic import TypeAdapter, ValidationError

from models.scenario import IncomingTrainUnit, TaskSpec, TrainUnit, TrainUnitType
from models.scenario_config import (
    CustomTrainsConfig,
    GeneratedTrainsConfig,
    ScenarioConfig,
    TrainUnitDistribution,
)

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
        base = TrainUnit(type_prefix="VIRM", carriages=6, id=2401)
        incoming = IncomingTrainUnit.from_train_unit(base)
        assert incoming.type_prefix == "VIRM"
        assert incoming.carriages == 6
        assert incoming.id == 2401


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


class TestScenarioConfig:
    """The configuration files are the only pipeline input written by hand, and
    check_config.py accepts any key it does not recognise — so a mistyped
    optional key has always been ignored rather than reported. These cover the
    part of that gap the model closes."""

    def test_trains_given_selects_the_custom_form(self):
        config = TypeAdapter(ScenarioConfig).validate_python({
            "location": "loc", "start_time": 0, "end_time": 3600,
            "use_default_material": True, "perform_servicing": False,
            "trains_given": True, "custom_trains": [], "custom_train_units": [],
        })
        assert isinstance(config, CustomTrainsConfig)

    def test_trains_given_false_selects_the_generated_form(self):
        config = TypeAdapter(ScenarioConfig).validate_python({
            "location": "loc", "start_time": 0, "end_time": 3600,
            "use_default_material": True, "perform_servicing": False,
            "trains_given": False, "number_of_trains": 4, "seed": 1,
        })
        assert isinstance(config, GeneratedTrainsConfig)

    def test_a_mistyped_optional_key_is_rejected(self):
        with pytest.raises(ValidationError):
            TypeAdapter(ScenarioConfig).validate_python({
                "location": "loc", "start_time": 0, "end_time": 3600,
                "use_default_material": True, "perform_servicing": False,
                "trains_given": False, "min_time_in_yards": 600,
            })

    def test_the_camelcase_standing_ratios_are_rejected(self):
        """scenario_config_test.json carried inStanding_ratio/outStanding_ratio,
        which random_generator.py never reads, so they quietly did nothing."""
        with pytest.raises(ValidationError):
            TrainUnitDistribution(train_unit_types=["VIRM-4"], inStanding_ratio=0.3)

    def test_intent_is_a_declared_field_not_a_tolerated_extra(self):
        config = TypeAdapter(ScenarioConfig).validate_python({
            "location": "loc", "start_time": 0, "end_time": 3600,
            "use_default_material": True, "perform_servicing": False,
            "trains_given": False,
            "intent": {"designed_for": "domain", "notes": ["a", "b"]},
        })
        assert config.intent.designed_for == "domain"
        assert config.intent.notes == ["a", "b"]

"""The values of the `matching` setting of a scenario configuration."""

import logging

FIFO = "FIFO"
RANDOM = "random"
LIFO = "LIFO"

MATCHING_NAMES = (FIFO, RANDOM, LIFO)

# Deprecated: until the integers are dropped, 0, 1 and 2 stand for these.
LEGACY_MATCHING_VALUES = {0: FIFO, 1: RANDOM, 2: LIFO}


def is_legacy_matching(value):
    """Whether value is one of the deprecated integers (a bool is not one)."""
    return isinstance(value, int) and not isinstance(value, bool) and value in LEGACY_MATCHING_VALUES


def matching_name(value):
    """The name (FIFO, random or LIFO) for a `matching` value, which is a name or a deprecated integer.

    Raises ValueError for anything else.
    """
    if value in MATCHING_NAMES and isinstance(value, str):
        return value
    if is_legacy_matching(value):
        return LEGACY_MATCHING_VALUES[value]
    raise ValueError(f"'matching' should be one of {', '.join(MATCHING_NAMES)} (got {value!r}).")


def normalize_matching_setting(config):
    """Validate config["matching"] in place and replace it by its name; random when absent.

    A deprecated integer is accepted, with a warning. Returns False (after logging an error) when the
    value is not valid.
    """
    if "matching" not in config:
        config["matching"] = RANDOM
        return True
    try:
        name = matching_name(config["matching"])
    except ValueError as e:
        logging.error(str(e))
        return False
    if is_legacy_matching(config["matching"]):
        logging.warning(
            f"'matching': {config['matching']} is deprecated and will stop being accepted in a later release; "
            f"use '{name}' (one of {', '.join(MATCHING_NAMES)})."
        )
    config["matching"] = name
    return True

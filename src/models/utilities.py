from pydantic import BaseModel, ConfigDict


class RailModel(BaseModel):
    """Base class for all interchange models.

    Forbids extra fields by default so that schema violations are caught
    at parse time rather than silently ignored. Use model_config to override
    in subclasses where forward-compatibility requires laxer reading.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class TimeInterval(RailModel):
    """A single time interval, with times in seconds since the epoch."""

    start: float
    end: float




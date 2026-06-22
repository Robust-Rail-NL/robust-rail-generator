from pydantic import BaseModel, ConfigDict


class RailModel(BaseModel):
    """Base class for all interchange models.

    Forbids extra fields by default so that schema violations are caught
    at parse time rather than silently ignored. Use model_config to override
    in subclasses where forward-compatibility requires laxer reading.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    def to_dict(self) -> dict:
        """Serialise to a dictionary suitable for JSON interchange.

        Uses camelCase field names (by_alias=True) and omits fields that
        were never explicitly set (exclude_unset=True), so optional fields
        absent from the original data do not appear as null or empty lists.
        """
        return self.model_dump(by_alias=True, exclude_unset=True)

    def to_json(self, **kwargs) -> str:
        """Serialise to a JSON string suitable for interchange.

        Accepts any keyword arguments supported by model_dump_json, but
        always applies by_alias=True and exclude_unset=True.
        """
        return self.model_dump_json(by_alias=True, exclude_unset=True, **kwargs)


class TimeInterval(RailModel):
    """A single time interval, with times in seconds since the epoch."""

    start: float
    end: float

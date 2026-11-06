"""Necessary conditions for a servicing scenario to be solvable.

Every bound here must hold for *any* solution, whichever way departures are matched to arrivals.
A violation therefore proves the scenario infeasible. Passing proves nothing: a scenario can pass
every bound and still be infeasible (shunting, routing and track capacity are not modelled).

Model: a facility with `simultaneousUsageCount` c serves at most c shunting units at once, and a
Service action occupies one of those places for the cumulative duration of all the tasks it
performs. So the place-seconds demanded of a facility type are the sum of the durations of all
tasks that use it, and c places supply c seconds per second. Facility availability windows
('timeWindow') are ignored: facilities are assumed always available.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Violation:
    """One violated bound. `train_id` is None for a bound over the whole scenario."""

    facility_type: str
    train_id: int | None
    required: float  # seconds needed (demand / capacity, plus travel allowance)
    available: float  # seconds available in the window
    description: str


def facility_capacities(location: dict) -> dict[str, int]:
    """Facility type -> total simultaneous usage over all facilities of that type."""
    capacities: dict[str, int] = {}
    for facility in location.get("facilities", []):
        capacities[facility["type"]] = capacities.get(facility["type"], 0) + facility.get("simultaneousUsageCount", 1)
    return capacities


def _task_facility_types(location: dict) -> dict[str, str]:
    """Task type name -> facility type that performs it."""
    mapping: dict[str, str] = {}
    for facility in location.get("facilities", []):
        for task_type in facility.get("taskTypes", []):
            name = task_type.get("other") or task_type.get("predefined")
            if name is not None:
                mapping[name] = facility["type"]
    return mapping


def _demand_per_train(scenario: dict, location: dict) -> dict[int, dict[str, int]]:
    """Incoming train id -> facility type -> summed task duration of its members."""
    task_to_facility = _task_facility_types(location)
    demand: dict[int, dict[str, int]] = {}
    for train in scenario.get("in", []):
        per_facility = demand.setdefault(train["id"], {})
        for member in train.get("members", []):
            for task in member.get("tasks") or []:
                name = task["type"].get("other") or task["type"].get("predefined")
                facility_type = task_to_facility.get(name)
                if facility_type is None:
                    continue  # no facility performs it: not a capacity question
                per_facility[facility_type] = per_facility.get(facility_type, 0) + task["duration"]
    return demand


def check_servicing_bounds(scenario: dict, location: dict, travel_allowance: int = 0) -> list[Violation]:
    """Return the violated necessary bounds of a scenario (JSON dict) at a location (JSON dict).

    Two bounds per facility type with capacity c and demand D:
    - Scenario: D_total / c <= latest departure - earliest arrival of a train that needs it.
    - Single train: when only one train arrives, D_train / c + travel_allowance <= its own
      window (departure of the one outgoing train - arrival). With several trains the
      matching decides which departure a unit leaves with, so no per-train bound is sound.

    `travel_allowance` is added only to the single-train bound. The default 0 keeps the check
    strictly necessary; a positive value is a heuristic for the movement to and from the facility.
    """
    capacities = facility_capacities(location)
    demand = _demand_per_train(scenario, location)
    arrivals = {train["id"]: train["arrival"] for train in scenario.get("in", [])}
    departures = [train["departure"] for train in scenario.get("out", [])]
    if not arrivals or not departures:
        return []
    latest_departure = max(departures)
    violations: list[Violation] = []

    for facility_type, capacity in capacities.items():
        needing = [tid for tid, per_facility in demand.items() if per_facility.get(facility_type, 0) > 0]
        if not needing:
            continue
        total = sum(demand[tid][facility_type] for tid in needing)
        window = latest_departure - min(arrivals[tid] for tid in needing)
        if total / capacity > window:
            violations.append(
                Violation(
                    facility_type,
                    None,
                    total / capacity,
                    window,
                    f"{facility_type}: {total}s of tasks over capacity {capacity} needs {total / capacity:.0f}s, "
                    f"but only {window}s lie between the first arrival that needs it and the last departure.",
                )
            )
        if len(arrivals) == 1 and len(departures) == 1:
            tid = needing[0]
            needed = demand[tid][facility_type] / capacity + travel_allowance
            window = departures[0] - arrivals[tid]
            if needed > window:
                violations.append(
                    Violation(
                        facility_type,
                        tid,
                        needed,
                        window,
                        f"{facility_type}: train {tid} needs {needed:.0f}s "
                        f"({demand[tid][facility_type]}s / capacity {capacity} + {travel_allowance}s travel), "
                        f"but is in the yard for {window}s.",
                    )
                )
    return violations

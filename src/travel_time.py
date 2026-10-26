"""How long a unit needs to drive from a gateway to a facility and out to a gateway again.

Prices a route with the movement model of the evaluator and the solver: a Move costs
`movementTrackCoefficient` for every track part of positive length on its path (the start track
included) and `movementSwitchCoefficient` for every switch crossed (an English switch counts
twice); a turn-around costs one more track crossing plus the unit's reversal duration. The
coefficients come from the location, defaulting to the values every location so far uses.

This is the travel alone. It leaves out waiting for other trains and the service itself, so it is
a lower bound for one unit alone in the yard.
"""

import heapq
import itertools

from robust_rail_models.location import TrackPartType

DEFAULT_TRACK_COEFFICIENT = 60
DEFAULT_SWITCH_COEFFICIENT = 30
SWITCH_COST = {
    TrackPartType.SWITCH: 1,
    TrackPartType.ENGLISH_SWITCH: 2,
    TrackPartType.HALF_ENGLISH_SWITCH: 2,
}
A, B = "a", "b"


def _other(side):
    return B if side == A else A


def _neighbours(track, heading):
    return track.a_side if heading == A else track.b_side


def _entry_heading(track, came_from):
    """The heading of a train that enters `track` from the neighbour `came_from`: it leaves through the other side."""
    if came_from in track.a_side:
        return B
    if came_from in track.b_side:
        return A
    return None


def _crossing_cost(track, track_coefficient, switch_coefficient):
    cost = SWITCH_COST.get(track.type, 0) * switch_coefficient
    if track.length and track.length > 0:
        cost += track_coefficient
    return cost


def servicing_travel_time(
    track_parts,
    facility_track_ids,
    arrival_gateways,
    departure_gateways,
    reversal_duration,
    track_coefficient=DEFAULT_TRACK_COEFFICIENT,
    switch_coefficient=DEFAULT_SWITCH_COEFFICIENT,
):
    """Seconds for the longest of the gateway-to-facility-to-gateway trips, or None if some trip has no route.

    `arrival_gateways` and `departure_gateways` are the generator's (gateway track part, bumper
    track part) pairs. A trip starts at the gateway heading away from its bumper, goes to the
    cheapest of the facility's tracks, and ends on a departure gateway heading for its bumper.
    Trips differ by which gateways are drawn, so the result is the longest over all pairs of
    arrival and departure gateways, each at its cheapest facility track.
    """
    by_id = {t.id: t for t in track_parts}
    facility_tracks = {t for t in facility_track_ids if t in by_id}
    goals = {}
    for gateway, bumper in departure_gateways:
        heading = A if bumper.id in gateway.a_side else B
        goals[gateway.id] = heading

    longest = 0
    for gateway, bumper in arrival_gateways:
        # The train arrives from the bumper, so it heads away from it.
        start_heading = B if bumper.id in gateway.a_side else A
        start_cost = _crossing_cost(gateway, track_coefficient, switch_coefficient)
        distance = _shortest(
            by_id, facility_tracks, (gateway.id, start_heading, 0), start_cost, reversal_duration,
            track_coefficient, switch_coefficient,
        )
        for goal_track, goal_heading in goals.items():
            cost = distance.get((goal_track, goal_heading, 1))
            if cost is None:
                return None
            longest = max(longest, cost)
    return longest


def _shortest(by_id, facility_tracks, start, start_cost, reversal_duration, track_coefficient, switch_coefficient):
    """Dijkstra over (track, heading, visited facility) states; returns the cost to every state reached."""
    best = {start: start_cost}
    counter = itertools.count()
    queue = [(start_cost, next(counter), start)]
    while queue:
        cost, _, state = heapq.heappop(queue)
        if cost > best[state]:
            continue
        track_id, heading, visited = state
        track = by_id[track_id]
        moves = []
        for neighbour_id in _neighbours(track, heading):
            neighbour = by_id.get(neighbour_id)
            if neighbour is None:
                continue
            new_heading = _entry_heading(neighbour, track_id)
            if new_heading is None:
                continue
            step = _crossing_cost(neighbour, track_coefficient, switch_coefficient)
            moves.append((cost + step, (neighbour_id, new_heading, visited)))
        if track.saw_movement_allowed:
            moves.append((cost + track_coefficient + reversal_duration, (track_id, _other(heading), visited)))
        if not visited and track_id in facility_tracks:
            # The service happens here; leaving afterwards is a new Move starting on this track.
            restart = track_coefficient if track.length and track.length > 0 else 0
            moves.append((cost + restart, (track_id, heading, 1)))
        for new_cost, new_state in moves:
            if new_cost < best.get(new_state, float("inf")):
                best[new_state] = new_cost
                heapq.heappush(queue, (new_cost, next(counter), new_state))
    return best

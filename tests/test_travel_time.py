"""servicing_travel_time() prices the drive gateway -> facility -> gateway with the movement model of
the evaluator and the solver: a track of positive length costs the track coefficient, a switch the
switch coefficient (an English switch twice), a turn-around one more track crossing plus the
reversal duration. The generator uses it to leave a serviced unit time to reach its facility."""

from robust_rail_models.location import TrackPart

from travel_time import servicing_travel_time


def track(id, type, length, a_side=(), b_side=(), saw=False):
    return TrackPart.model_validate(
        {
            "id": id,
            "type": type,
            "aSide": list(a_side),
            "bSide": list(b_side),
            "length": length,
            "sawMovementAllowed": saw,
        }
    )


def yard():
    """bumper(0) - gate(1) - switch(2) - facility(3), plus a spur (4) off the switch."""
    return [
        track(0, "Bumper", 0, b_side=[1]),
        track(1, "RailRoad", 100, a_side=[0], b_side=[2], saw=True),
        track(2, "Switch", 0, a_side=[1], b_side=[3, 4]),
        track(3, "RailRoad", 200, a_side=[2], saw=True),
        track(4, "RailRoad", 100, a_side=[2], saw=True),
    ]


def gateway(tracks):
    return [(tracks[1], tracks[0])]


def test_a_round_trip_costs_every_crossing_and_one_turn_around():
    tracks = yard()

    travel = servicing_travel_time(tracks, [3], gateway(tracks), gateway(tracks), reversal_duration=100)

    # out: gate 60 + switch 30 + facility 60; the next Move starts on the facility, 60 again;
    # turn around there: 60 + 100; back: switch 30 + gate 60
    assert travel == 60 + 30 + 60 + 60 + (60 + 100) + 30 + 60


def test_the_coefficients_come_from_the_caller():
    tracks = yard()

    travel = servicing_travel_time(
        tracks, [3], gateway(tracks), gateway(tracks), reversal_duration=0, track_coefficient=10, switch_coefficient=5
    )

    assert travel == 10 + 5 + 10 + 10 + 10 + 5 + 10


def test_the_cheapest_of_a_facilitys_tracks_is_used():
    tracks = yard()

    both = servicing_travel_time(tracks, [3, 4], gateway(tracks), gateway(tracks), reversal_duration=100)
    only_far = servicing_travel_time(tracks, [3], gateway(tracks), gateway(tracks), reversal_duration=100)

    assert both <= only_far


def test_a_facility_with_no_route_gives_none():
    tracks = yard()
    tracks.append(track(9, "RailRoad", 100, saw=True))  # connected to nothing

    assert servicing_travel_time(tracks, [9], gateway(tracks), gateway(tracks), reversal_duration=100) is None


def test_a_facility_that_is_not_a_track_of_the_location_gives_none():
    tracks = yard()

    assert servicing_travel_time(tracks, [99], gateway(tracks), gateway(tracks), reversal_duration=100) is None

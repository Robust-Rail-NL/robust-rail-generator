import logging


def check_matching(scenario_generator, use_default_material=True, minimal_yard_time=600):
    valid = check_train_lengths(scenario_generator, use_default_material)
    if not valid:
        return False
    train_units = [
        (train, unit, "incoming") for train in scenario_generator.scenario.in_ for unit in (train.members)
    ] + [(train, unit, "instanding") for train in scenario_generator.scenario.in_standing for unit in train.members]
    train_unit_requests = [
        (train, unit, "outgoing") for train in scenario_generator.scenario.out for unit in train.members
    ] + [(train, unit, "outstanding") for train in scenario_generator.scenario.out_standing for unit in train.members]
    if len(train_units) != len(train_unit_requests):
        logging.warning(
            f"Number of incoming train units ({len(train_units)}) does not match number of outgoing train unit requests ({len(train_unit_requests)})."
        )
        return False
    # Check for duplicate times
    if len(set([train.time for train in scenario_generator.scenario.in_])) != len(scenario_generator.scenario.in_):
        logging.warning(
            "There are duplicate arrival times among incoming trains, which is not supported in this primitive matching check."
        )
        return False
    if len(set([train.time for train in scenario_generator.scenario.out])) != len(scenario_generator.scenario.out):
        logging.warning(
            "There are duplicate departure times among outgoing trains, which is not supported in this primitive matching check."
        )
        return False
    # Check for matching types
    if sorted([unit.type_display_name for _, unit, _ in train_units]) != sorted(
        [unit.type_display_name for _, unit, _ in train_unit_requests]
    ):
        logging.warning("Types of incoming train units do not match types of outgoing train unit requests.")
        return False
    for in_train, unit, _ in train_units:
        # Primitive matching does not use minimum yard time, because trains can also be delayed
        matching_departures = [
            (req_unit, out_train.time, typ)
            for out_train, req_unit, typ in train_unit_requests
            if req_unit.type_display_name == unit.type_display_name
            and (out_train.time > in_train.time + sum([t.duration for t in unit.tasks]) or typ == "outstanding")
        ]
        if not matching_departures:
            logging.warning(
                f"No matching departure found for incoming train unit {unit.id} of type {unit.type_display_name} arriving at {in_train.time} with train {in_train.id}."
            )
            return False
        # Remove the first matching departure to ensure one-to-one matching
        first_departing_train = min(matching_departures, key=lambda tuple: tuple[1])
        train_unit_requests.remove(
            (
                next(
                    out_train
                    for out_train, req_unit, typ in train_unit_requests
                    if req_unit.type_display_name == first_departing_train[0].type_display_name
                    and out_train.time == first_departing_train[1]
                    and typ == first_departing_train[2]
                ),
                first_departing_train[0],
                first_departing_train[2],
            )
        )
        logging.info(
            f"Primitively matched incoming train unit {unit.id} of type {unit.type_display_name} of train {in_train.id} arriving at {in_train.time} with departure at {first_departing_train[1]}."
        )
    if len(train_unit_requests) > 0:
        logging.warning(
            f"There are {len(train_unit_requests)} unmatched outgoing train unit requests remaining, which should not happen in this primitive matching check."
        )
        return False
    return True


def check_train_lengths(scenario_generator, use_default_material):
    type_lengths = {t.type_display_name: t.length for t in scenario_generator.scenario.train_unit_types}
    track_lengths = {
        t.name: t.length
        for t in scenario_generator.location.track_parts
        if t.parking_allowed and t.saw_movement_allowed
    }
    avg_track_length = sum(track_lengths.values()) / len(track_lengths.values())
    long_trains = []
    # Also do a check for trains that are too long
    for train in scenario_generator.scenario.in_:
        length = sum([type_lengths[unit.type_display_name] for unit in train.members])
        if length > max(track_lengths.values()):
            logging.warning(
                f"Length of train {train.id} with {len(train.members)} units is {length} and exceeds length of longest track is {avg_track_length}"
            )
            return False
        if use_default_material:
            carriages = sum([unit.carriages for unit in train.members])
            if carriages > 12:
                logging.warning(
                    f"Train {train.id} has {carriages} carriages, which exceeds the default 12 for train in the Netherlands with default train unit types."
                )
                return False
        if length > avg_track_length:
            long_trains.append((train, length))
    long_trains.sort(key=lambda x: x[1])
    for train, length in long_trains:
        longest_track = [
            (t, track_length)
            for t, track_length in track_lengths.items()
            if track_length == max(track_lengths.values())
        ]
        if length > longest_track[0][1]:
            logging.warning(
                f"Train {train.id} has length {length}, which exceeds the longest available track {longest_track[0]} of length {longest_track[1]}."
            )
            return False
        else:
            logging.info(
                f"Primitively assigned train {train.id} to track {longest_track[0][0]} of length {longest_track[0][1]}"
            )
            track_lengths.pop(longest_track[0][0])
    return True

import logging

def check_matching(scenario_generator, use_default_material=True, minimal_yard_time=600):
    valid = check_train_lengths(scenario_generator, use_default_material)
    if not valid:
        return False
    train_units = [(train, unit, "incoming") for train in getattr(scenario_generator.scenario, "in") for unit in train.members] + [(train, unit, "instanding") for train in getattr(scenario_generator.scenario, "inStanding") for unit in train.members]
    train_unit_requests = [(train, unit, "outgoing") for train in getattr(scenario_generator.   scenario, "out") for unit in train.members] + [(train, unit, "outstanding") for train in getattr(scenario_generator.scenario, "outStanding") for unit in train.members]
    if len(train_units) != len(train_unit_requests):
        logging.warning(f"Number of incoming train units ({len(train_units)}) does not match number of outgoing train unit requests ({len(train_unit_requests)}).")
        return False
    # Check for duplicate times
    if len(set([train.time for train in getattr(scenario_generator.scenario, "in")])) != len(getattr(scenario_generator.scenario, "in")):
        logging.warning("There are duplicate arrival times among incoming trains, which is not supported in this primitive matching check.")
        return False
    if len(set([train.time for train in getattr(scenario_generator.scenario, "out")])) != len(getattr(scenario_generator.scenario, "out")):
        logging.warning("There are duplicate departure times among outgoing trains, which is not supported in this primitive matching check.")
        return False
    # Check for matching types
    if sorted([unit.typeDisplayName for _, unit, _ in train_units]) != sorted([unit.typeDisplayName for _, unit, _ in train_unit_requests]):
        logging.warning("Types of incoming train units do not match types of outgoing train unit requests.")
        return False
    for in_train, unit, _ in train_units:
        matching_departures = [(req_unit, out_train.time, typ) for out_train, req_unit, typ in train_unit_requests if req_unit.typeDisplayName == unit.typeDisplayName and out_train.time >= in_train.time + minimal_yard_time]
        if not matching_departures:
            logging.warning(f"No matching departure found for incoming train unit {unit.id} of type {unit.typeDisplayName} arriving at {in_train.time} with train {in_train.id}.")
            return False
        # Remove the first matching departure to ensure one-to-one matching
        first_departing_train = min(matching_departures, key=lambda tuple: tuple[1])
        train_unit_requests.remove((next(out_train for out_train, req_unit, typ in train_unit_requests if req_unit.typeDisplayName == first_departing_train[0].typeDisplayName and out_train.time == first_departing_train[1] and typ == first_departing_train[2]), first_departing_train[0], first_departing_train[2]))
        logging.info(f"Primitively matched incoming train unit {unit.id} of type {unit.typeDisplayName} of train {in_train.id} arriving at {in_train.time} with departure at {first_departing_train[1]}.")
    if len(train_unit_requests) > 0:
        logging.warning(f"There are {len(train_unit_requests)} unmatched outgoing train unit requests remaining, which should not happen in this primitive matching check.")
        return False
    return True

def check_train_lengths(scenario_generator, use_default_material):
    type_lengths = {t.displayName: t.length for t in getattr(scenario_generator.scenario, "trainUnitTypes")}
    track_lengths = {t.name: t.length for t in getattr(scenario_generator.location, "trackParts") if t.parkingAllowed and t.sawMovementAllowed}
    avg_track_length = sum(track_lengths.values()) / len(track_lengths.values())
    long_trains = []
    # Also do a check for trains that are too long
    for train in getattr(scenario_generator.scenario, "in"):
        length = sum([type_lengths[unit.typeDisplayName] for unit in train.members])
        if length > max(track_lengths.values()):
            logging.warning(f"Length of train {train.id} with {len(train.members)} units is {length} and exceeds length of longest track is {avg_track_length}")
            return False
        if use_default_material:
            carriages = sum([int(unit.typeDisplayName.split("-")[1]) for unit in train.members])
            if carriages > 12:
                logging.warning(f"Train {train.id} has {carriages} carriages, which exceeds the default 12 for train in the Netherlands with default train unit types.")
                return False
        if length > avg_track_length:
            long_trains.append((train, length))
    long_trains.sort(key=lambda x: x[1])
    for train, length in long_trains:
        longest_track = [(t, l) for t, l in track_lengths.items() if l == max(track_lengths.values())]
        if length > longest_track[0][1]:
            logging.warning(f"Train {train.id} has length {length}, which exceeds the longest available track {longest_track[0]} of length {longest_track[1]}.")
            return False
        else:
            logging.info(f"Primitively assigned train {train.id} to track {longest_track[0][0]} of length {longest_track[0][1]}")
            track_lengths.pop(longest_track[0][0])
    return True
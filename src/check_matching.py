import logging

def check_matching(scenario, minimal_yard_time=600):
    train_units = [(train, unit, "incoming") for train in getattr(scenario, "in") for unit in train.members] + [(train, unit, "instanding") for train in getattr(scenario, "inStanding") for unit in train.members]
    train_unit_requests = [(train, unit, "outgoing") for train in getattr(scenario, "out") for unit in train.members] + [(train, unit, "outstanding") for train in getattr(scenario, "outStanding") for unit in train.members]
    if len(train_units) != len(train_unit_requests):
        logging.warning(f"Number of incoming train units ({len(train_units)}) does not match number of outgoing train unit requests ({len(train_unit_requests)}).")
        return False
    # Check for duplicate times
    if len(set([train.time for train in getattr(scenario, "in")])) != len(getattr(scenario, "in")):
        logging.warning("There are duplicate arrival times among incoming trains, which is not supported in this primitive matching check.")
        return False
    if len(set([train.time for train in getattr(scenario, "out")])) != len(getattr(scenario, "out")):
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

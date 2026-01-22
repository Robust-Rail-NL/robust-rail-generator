import math
import random
import logging
from copy import deepcopy

from py_protobuf.Location_pb2 import TrackPartType

class RandomGenerator:
    def __init__(self, gen, config, location, gateways):
        """Initialize the random generator for a specific scenario generator."""
        self.scenario_generator = gen
        self.seed = config["seed"]
        random.seed(self.seed)
        self.train_unit_types = []
        self.train_units = {}
        self.train_units_subtypes = {}
        self.number_of_train_units = 0
        self.trains = []
        self.gateways = gateways
        possible_gateways = self.get_gateway_tracks(config, location)
        if len(self.gateways["arrival"]) == 0:
            self.gateways["arrival"] = possible_gateways
        if len(self.gateways["departure"]) == 0:
            self.gateways["departure"] = possible_gateways
    
    def reset(self):
        """Reset the random generator to its initial state."""
        logging.info("Resetting the random generator to its initial state. Keeping the gateways the same.")
        self.train_unit_types = []
        self.train_units = {}
        self.train_units_subtypes = {}
        self.number_of_train_units = 0
        self.trains = []
        self.scenario_generator.scenario.ClearField("in")
        self.scenario_generator.scenario.ClearField("out")
        self.scenario_generator.scenario.ClearField("inStanding")
        self.scenario_generator.scenario.ClearField("outStanding")

    def get_gateway_tracks(self, config, location):
        gateways = []
        facilities = [t for f in location.facilities for t in f.relatedTrackParts]
        for track in location.trackParts:
            if track.type == TrackPartType.RailRoad:
                bumper_a = [config["track_id_map"][a].id
                            for a in track.aSide 
                            if config["track_id_map"][a].type == TrackPartType.Bumper]
                bumper_b = [config["track_id_map"][b].id
                            for b in track.bSide 
                            if config["track_id_map"][b].type == TrackPartType.Bumper]
                if len(bumper_a) == 0 and len(bumper_b) == 1:
                    if config["track_id_map"][bumper_b[0]].aSide:
                        gateway = config["track_id_map"][config["track_id_map"][bumper_b[0]].aSide[0]]
                    else:
                        logging.error(f"Bumper {config['track_id_map'][bumper_b[0]].id} on the B-side of track {track.id} does not have this track on its own A-side.")
                    if config["track_id_map"][bumper_b[0]].bSide:
                        logging.error(f"Bumper {config['track_id_map'][bumper_b[0]].id} on the B-side of track {track.id} has a track part with id {config['track_id_map'][bumper_b[0]].bSide[0]} on its B-side.")
                    if gateway not in gateways and gateway.type == TrackPartType.RailRoad and not gateway.stationPlatform and gateway.id not in facilities and gateway.sawMovementAllowed and not gateway.parkingAllowed and gateway.length > 0:
                        gateways.append((gateway, config["track_id_map"][bumper_b[0]]))
                        logging.info(f"Found gateway track {gateway.name}")
                elif len(bumper_a) == 1 and len(bumper_b) == 0:
                    if config["track_id_map"][bumper_a[0]].bSide:
                        gateway = config["track_id_map"][config["track_id_map"][bumper_a[0]].bSide[0]]
                    else:
                        logging.error(f"Bumper {config['track_id_map'][bumper_a[0]].id} on the A-side of track {track.id} does not have this track on its own B-side.")
                    if config["track_id_map"][bumper_a[0]].aSide:
                        logging.error(f"Bumper {config['track_id_map'][bumper_a[0]].id} on the A-side of track {track.id} has a track part with id {config['track_id_map'][bumper_a[0]].aSide[0]} on the B-side.")
                    if gateway not in gateways and gateway.type == TrackPartType.RailRoad and not gateway.stationPlatform and gateway.id not in facilities and gateway.sawMovementAllowed and not gateway.parkingAllowed  and gateway.length > 0:
                        gateways.append((gateway, config["track_id_map"][bumper_a[0]]))
                        logging.info(f"Found gateway track {gateway.name}")
        return gateways

    def generate_train_compositions(self, config, scenario_generator):
        distribution_config = {"number_trains_in": config["number_of_trains"], "number_trains_out": config["number_of_trains"], "min_time_in_yard": config["min_time_in_yard"], "min_gap_on_gateway": config["min_gap_on_gateway"], "mixed_traffic": config["mixed_traffic"], "matching": config["matching"]}
        number_train_units = 0
        if "train_unit_distribution" in config:
            # If a specific sublist of train unit types was provided, update the possible train unit types
            if "train_unit_types" in config["train_unit_distribution"]:
                scenario_generator.scenario_TrainUnitTypes = [u for u in scenario_generator.scenario_TrainUnitTypes if u.displayName in config["train_unit_distribution"]["train_unit_types"]]
                self.train_unit_types = scenario_generator.scenario_TrainUnitTypes.copy()
                self.train_units_subtypes = {u.displayName.split("-")[0]: [sub.displayName for sub in self.train_unit_types if u.displayName.split("-")[0] in sub.displayName] for u in self.train_unit_types}
            # If a distribution of train units over the trains was given, use this for the train creation
            distribution_config.update(config["train_unit_distribution"])
            # Decide the number of units per train
            distribution_config["number_units_per_in_train"] = [random.choice(distribution_config["units_per_composition"]) for _ in range(config["number_of_trains"])]
            # For each train, randomly sample the number of units from the decided number of units
            different_types = min(len(self.train_units_subtypes), math.floor(config["number_of_trains"] * distribution_config["super_type_ratio"]) + 1)
            # This is an array with for each train the supertype it will be assigned to
            distribution_config["super_types_in_train"] = [range(different_types)[i % different_types] for i in range(config["number_of_trains"])]
            random.shuffle(distribution_config["super_types_in_train"])

            # Ensure that trains with subtypes of 6 carriages do not have more than 2 units
            for i, t in enumerate(distribution_config["super_types_in_train"]):
                super_type = list(self.train_units_subtypes.keys())[t]
                if f"{super_type}-6" in self.train_units_subtypes[super_type] and distribution_config["number_units_per_in_train"][i] > 2:
                    distribution_config["number_units_per_in_train"][i] = 2

            # For each unit subtype we calculate the number of associated train units
            distribution_config["units_per_super_type"] = {t: sum([units for i, units in enumerate(distribution_config["number_units_per_in_train"]) if distribution_config["super_types_in_train"][i] == t]) for t in range(different_types)}
            super_types = list(self.train_units_subtypes.keys())

            # For each train, randomly sample the subtype for each unit from the supertype assigned to this train for the known number of units
            distribution_config["subtypes_per_in_train"] = [[random.choice(self.train_units_subtypes[super_types[t]]) for _ in range(distribution_config["number_units_per_in_train"][j])] for j, t in enumerate(distribution_config["super_types_in_train"])]
            # Calculate the number of units per subtype
            distribution_config["number_subtype_units"] = {sub: sum([1 for train in distribution_config["subtypes_per_in_train"] for u in train if u == sub]) for sub in set([u for train in distribution_config["subtypes_per_in_train"] for u in train])}
            # This is an array of all the train units, where each item is the subtype of the unit
            distribution_config["unit_types"] = [u for train in distribution_config["subtypes_per_in_train"] for u in train]
            number_train_units = len(distribution_config["unit_types"])

            if distribution_config["matching"] == 0:
                # Same arrival and distribution compositions
                distribution_config["subtypes_per_out_train"] = deepcopy(distribution_config["subtypes_per_in_train"])
            elif distribution_config["matching"] == 1:
                # Redistribute the incoming train units over the outgoing trains
                subtypes_per_super_type = {t: [sub for sub in distribution_config["unit_types"] if t in sub] for t in super_types}
                distribution_config["subtypes_per_out_train"] = []
                for sup_type in subtypes_per_super_type:
                    while len(subtypes_per_super_type[sup_type]) > 0:
                        if len(subtypes_per_super_type[sup_type]) > max(distribution_config["units_per_composition"]):
                            num_units = random.choice(distribution_config["units_per_composition"])
                        else:
                            num_units = len(subtypes_per_super_type[sup_type])
                        new_train = []
                        for _ in range(num_units):
                            new_train.append(subtypes_per_super_type[sup_type].pop())
                        distribution_config["subtypes_per_out_train"].append(new_train)
                distribution_config["number_trains_out"] = len(distribution_config["subtypes_per_out_train"])
            elif distribution_config["matching"] == 2:
                # Assume last in last out
                distribution_config["subtypes_per_out_train"] = deepcopy(distribution_config["subtypes_per_in_train"])
                distribution_config["subtypes_per_out_train"].reverse()
        elif config["use_default_material"]:
            # For each train to be generated, randomly sample its type and give it a random number of units between 1 and 3 (upper limit not included in randrange)
            distribution_config.update({"unit_types_per_train": [(random.choice(self.train_unit_types), random.randrange(1, 4, 1)) for _ in range(config["number_of_trains"])]})
            number_train_units = sum([num for _, num in distribution_config["unit_types_per_train"]])
        else:
            # For each train to be generated, randomly sample its type and give it a random number of units between 1 and 3 (upper limit not included in randrange)
            distribution_config.update({"unit_types_per_train": [(random.choice(self.train_unit_types), random.randrange(1, 4, 1)) for _ in range(config["number_of_trains"])]})
            number_train_units = sum([num for _, num in distribution_config["unit_types_per_train"]])
        self.generate_train_units(number_train_units, config["perform_servicing"], distribution_config)
        self.generate_trains(config, distribution_config)
        
    def generate_train_unit_types(self, num: int):
        for i in range(num):
            unit_type = self.scenario_generator.create_TrainUnitType(
                displayName=f"unitType{i}",
                carriages=random.randrange(3, 8),
                length=random.randrange(40, 160, 5),
                combineDuration=random.randrange(0, 600, 10),
                splitDuration=random.randrange(0, 600, 10),
                backNormTime=random.randrange(0, 600, 10),
                backAdditionTime=random.randrange(0, 600, 10),
                travelSpeed=random.randrange(50, 300, 10), # assumed km/h
                startUpTime=random.randrange(0, 600, 10),
                needsLoco=False, # assumed
                isLoco=False, # assumed
                needsElectricity=True, # assumed
                typePrefix="random",
            )
            self.train_unit_types.append(unit_type)
            self.scenario_generator.add_TrainUnitType(unit_type)

    def generate_train_units(self, number_train_units, servicing, distribution_config):
        random.shuffle(self.train_unit_types)
        for i in range(number_train_units):
            # TODO servicing tasks
            if not distribution_config:
                logging.warning("No distribution config provided, number of train units cannot be simply distributed over number of trains")
            else:
                if "unit_types" in distribution_config:
                    unit_type = distribution_config["unit_types"][i]
                else:
                    # Use the generate unit distribution
                    idx = 0
                    for typ, num in distribution_config["unit_types_per_train"]:
                        idx += num
                        if i < idx:
                            unit_type = typ.displayName
                            break
            if not servicing:
                unit = self.scenario_generator.create_TrainUnit(
                    id=str(i),
                    typeDisplayName=unit_type,
                    tasks=[]
                )
                if unit_type not in self.train_units:
                    self.train_units[unit_type] = []
                self.train_units[unit_type].append(unit)
                self.number_of_train_units += 1
        if self.number_of_train_units != number_train_units:
            logging.error(f"Expected {number_train_units} train units and {self.number_of_train_units} were created")

    def generate_trains(self, config, distribution_config):
        distribution_in, distribution_out = self.distribute_train_units(distribution_config)
        arrival_times, departure_times = self.assign_arrival_departure_times(distribution_config)
        # Check for instanding and outstanding trains
        instanding_train_ids = random.sample(range(distribution_config["number_trains_in"]), math.floor(distribution_config["number_trains_in"] * distribution_config.get("instanding_ratio"))) if distribution_config and "instanding_ratio" in distribution_config else []
        outstanding_train_ids = random.sample(range(distribution_config["number_trains_in"], distribution_config["number_trains_in"]+distribution_config["number_trains_out"]), math.floor(distribution_config["number_trains_out"] * distribution_config.get("outstanding_ratio"))) if distribution_config and "outstanding_ratio" in distribution_config else []
        parking_tracks_instanding = random.sample([tr for tr in self.scenario_generator.location.trackParts if tr.parkingAllowed and tr.id not in self.gateways["arrival"]], len(instanding_train_ids))
        parking_tracks_outstanding = random.sample([tr for tr in self.scenario_generator.location.trackParts if tr.parkingAllowed and tr.id not in self.gateways["departure"]], len(outstanding_train_ids))
        standing_trains = {"instanding": {id: parking_tracks_instanding[j] for j, id in enumerate(instanding_train_ids)}, "outstanding": {id: parking_tracks_outstanding[j] for j, id in enumerate(outstanding_train_ids)}}
        ### Create train objects
        for (i, train_units) in enumerate(distribution_in):
            ### Incoming train
            if i in standing_trains["instanding"]:
                train_in = self.scenario_generator.create_Train(
                    id=str(i),
                    time=self.scenario_generator.scenario.startTime,
                    members=train_units,
                    standingIndex=1,
                    sideTrackPart=standing_trains["instanding"][i].aSide[0] if len(config["track_id_map"][standing_trains["instanding"][i].aSide[0]].aSide) == 0 else standing_trains["instanding"][i].bSide[0],
                    trackPart=standing_trains["instanding"][i].id,
                    canDepartFromAnyTrack=True,
                    minimumDuration="60"
                )
                self.scenario_generator.add_inStandingTrain(train_in)
            else:
                gateway, side = random.choice(self.gateways["arrival"])
                train_in = self.scenario_generator.create_Train(
                    id=str(i),
                    time=arrival_times[i],
                    members=train_units,
                    sideTrackPart=side.id,
                    trackPart=gateway.id,
                    canDepartFromAnyTrack=False,
                    minimumDuration="60"
                )
                self.scenario_generator.add_incomingTrain(train_in)
            self.trains.append(train_in)
        id_offset = distribution_config["number_trains_in"]
        for (i, train_units) in enumerate(distribution_out):
            ### Outgoing train
            unmatched_train_units = [self.scenario_generator.create_TrainUnitUnmatchedMembers(train_unit.typeDisplayName) for train_unit in train_units]
            if i+id_offset in standing_trains["outstanding"]:
                train_out = self.scenario_generator.create_Train(
                    id=f"{i+id_offset}",
                    time=self.scenario_generator.scenario.endTime,
                    members=unmatched_train_units,
                    standingIndex=1,
                    sideTrackPart=standing_trains["outstanding"][i+id_offset].aSide[0] if len(config["track_id_map"][standing_trains["outstanding"][i+id_offset].aSide[0]].aSide) == 0 else standing_trains["outstanding"][i+id_offset].bSide[0],
                    trackPart=standing_trains["outstanding"][i+id_offset].id,
                    canDepartFromAnyTrack=True,
                    minimumDuration="60"
                )
                self.scenario_generator.add_outStandingTrain(train_out)
            else:
                gateway, side = random.choice(self.gateways["departure"])
                train_out = self.scenario_generator.create_Train(
                    id=f"{i+id_offset}",
                    time=departure_times[i],
                    members=unmatched_train_units,
                    standingIndex=1, # assume
                    sideTrackPart=side.id,
                    trackPart=gateway.id,
                    canDepartFromAnyTrack=False,
                    minimumDuration="60"
                )
                self.scenario_generator.add_outgoingTrain(train_out)
            self.trains.append(train_out)

    def assign_arrival_departure_times(self, distribution_config):
        arrival_times = []
        departure_times = []
        # Mixed traffic allows trains to depart before all trains have arrived
        if distribution_config["mixed_traffic"]:
            # Arrive in 2/3 of total time - generate 
            arrival_times = random.sample(range(self.scenario_generator.scenario.startTime, math.floor(self.scenario_generator.scenario.endTime * 2 / 3), distribution_config["min_gap_on_gateway"]), distribution_config["number_trains_in"])
            possible_departure_times = [t for t in range(min(arrival_times) + distribution_config["min_time_in_yard"], self.scenario_generator.scenario.endTime, distribution_config["min_gap_on_gateway"]) if t not in arrival_times]
            # TODO allow extra minimum servicing time
            for y in range(distribution_config["number_trains_out"]):
                # Possible that there are more departing trains then arriving
                try:
                    if y >= len(arrival_times):
                        departure_times.append(random.sample(possible_departure_times, 1)[0])
                    else:
                        # Make sure that the departure time is after the arrival time for at least one train
                        departure_times.append(random.sample([x for x in possible_departure_times if x > arrival_times[y]], 1)[0])
                    possible_departure_times.remove(departure_times[-1])
                except:
                    logging.error(f"Cannot sample departure time for train {y} from possible departure times after arrival time {arrival_times[y]} with min gap {distribution_config['min_gap_on_gateway']}. Possible departure times: {possible_departure_times}")
        else:
            # Arrive in first half of total time
            try:
                arrival_times = random.sample(range(self.scenario_generator.scenario.startTime, math.floor(self.scenario_generator.scenario.endTime / 2), distribution_config["min_gap_on_gateway"]), distribution_config["number_trains_in"])
            except:
                logging.error(f"Cannot sample {distribution_config['number_trains_in']} arrival times from range {self.scenario_generator.scenario.startTime} to {math.floor(self.scenario_generator.scenario.endTime / 2)} (endtime/2) with min gap {distribution_config['min_gap_on_gateway']}")
            # Depart in second half of total time
            try:
                departure_times = random.sample(range(math.floor(self.scenario_generator.scenario.endTime / 2), self.scenario_generator.scenario.endTime, distribution_config["min_gap_on_gateway"]), distribution_config["number_trains_out"])
            except:
                logging.error(f"Cannot sample {distribution_config['number_trains_out']} departure times from range {math.floor(self.scenario_generator.scenario.endTime / 2)} (endtime/2) to {self.scenario_generator.scenario.endTime} with min gap {distribution_config['min_gap_on_gateway']}")
        return arrival_times, departure_times 

    def distribute_train_units(self, distribution_config):
        if self.number_of_train_units < distribution_config["number_trains_in"] or self.number_of_train_units > 3 * distribution_config["number_trains_in"]:
            raise ValueError(f"Cannot make sure that all {distribution_config['number_trains_in']} trains get between 1 and 3 train units from {len(self.train_units)} units.")

        in_trains = [[] for _ in range(distribution_config["number_trains_in"])]
        out_trains = [[] for _ in range(distribution_config["number_trains_out"])]

        in_units = deepcopy(self.train_units)
        out_units = deepcopy(self.train_units)
        for typ in in_units:
            random.shuffle(in_units[typ])
            random.shuffle(out_units[typ])

        if "unit_types_per_train" in distribution_config:
            # For each train of a certain type, randomly select the train units part of this train for the predetermined number of units
            logging.info(f"Number of units per train is assigned, assigning the actual units to trains.")
            for i, (t, num) in enumerate(distribution_config["unit_types_per_train"]):
                for _ in range(num):
                    in_trains[i].append(in_units[t.displayName].pop())
            # Matching: 0 same order, 1: random order, 2: reverse order
            if distribution_config["matching"] == 1:
                random.shuffle(distribution_config["unit_types_per_train"])
            elif distribution_config["matching"] == 2:
                distribution_config["unit_types_per_train"].reverse()
            for i, (t, num) in enumerate(distribution_config["unit_types_per_train"]):
                for _ in range(num):
                    out_trains[i].append(out_units[t.displayName].pop())
        elif "subtypes_per_in_train" in distribution_config:
            # The number of units per train and its train type were already generated, so allocate the units.
            # This is the only method that allows train units of same supertype in one composition
            logging.info("Using the predefined subtypes and number of train units assigned per train to assign individual units.")
            for train_num, sub_type_list in enumerate(distribution_config["subtypes_per_in_train"]):
                for sub_type in sub_type_list:
                    in_trains[train_num].append(in_units[sub_type].pop())
            for train_num, sub_type_list in enumerate(distribution_config["subtypes_per_out_train"]):
                for sub_type in sub_type_list:
                    out_trains[train_num].append(out_units[sub_type].pop())                    
        else:
            # Without any prior knowledge, randomly distribute, though this is prone to vulnerabilities. 
            # Select number of trains per type
            logging.info("Randomly sample a number of units per train and select a type for this train.")
            for typ in in_units:
                number_trains_of_type = random.randint(math.ceil(len(in_units[typ]) / 3), math.floor(distribution_config["number_trains_in"] / len(in_units)))
                for _ in range(number_trains_of_type):
                    in_trains.append([in_units[typ].pop()])

            for unit_type in in_units:
                trains_of_type = {i: t for i, t in enumerate(in_trains) if t[0].typeDisplayName == unit_type}
                while in_units[unit_type]:
                    idx = random.randint(0, len(trains_of_type) - 1)
                    if len(trains_of_type[idx]) < 3 :
                        in_trains[idx].append(in_units[unit_type].pop())

            # Do the same for outgoing trains
            for typ in out_units:
                number_trains_of_type = random.randint(math.ceil(len(out_units[typ]) / 3), math.floor(distribution_config["number_trains_out"] / len(out_units)))
                for _ in range(number_trains_of_type):
                    out_trains.append([out_units[typ].pop()])
            for unit_type in out_units:
                trains_of_type = {i: t for i, t in enumerate(out_trains) if t[0].typeDisplayName == unit_type}
                while out_units[unit_type]:
                    idx = random.randint(0, len(trains_of_type) - 1)
                    if len(trains_of_type[idx]) < 3 :
                        out_trains[idx].append(out_units[unit_type].pop())
        if sum([len(in_units[t]) for t in in_units]) != 0 or sum([len(out_units[t]) for t in out_units]) != 0:
            logging.error(f"Not all train units were assigned to trains, {sum([len(in_units[t]) for t in in_units])} incoming and {sum([len(out_units[t]) for t in out_units])} outgoing units left")
        return in_trains, out_trains
    
    def resample_arrival_departure_times(self, scenario, distribution_config):
        arrival_times, departure_times = self.assign_arrival_departure_times(distribution_config)            
        for train in getattr(scenario, "in"):
            train.time = arrival_times[int(train.id)]
        for train in getattr(scenario, "out"):
            train.time = departure_times[int(train.id) - distribution_config["number_trains_in"]]

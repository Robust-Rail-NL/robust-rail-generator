import math
import random
import logging

from py_protobuf.Location_pb2 import TrackPartType

class RandomGenerator:
    def __init__(self, gen, seed, location, gateways):
        """Initialize the random generator for a specific scenario generator."""
        self.scenario_generator = gen
        self.seed = seed
        random.seed(self.seed)
        self.train_unit_types = []
        self.train_units = {}
        self.train_units_subtypes = {}
        self.number_of_train_units = 0
        self.trains = []
        self.gateways = gateways
        if len(self.gateways["arrival"]) == 0:
            self.gateways["arrival"] = self.get_gateway_tracks(location)
        if len(self.gateways["departure"]) == 0:
            self.gateways["departure"] = self.get_gateway_tracks(location)

    def get_gateway_tracks(self, location):
        gateways = []
        facilities = [t for f in location.facilities for t in f.relatedTrackParts]
        for track in location.trackParts:
            if track.type == TrackPartType.RailRoad:
                bumper_a = [location.trackParts[a].id 
                            for a in track.aSide 
                            if location.trackParts[a].type == TrackPartType.Bumper]
                bumper_b = [location.trackParts[b].id 
                            for b in track.bSide 
                            if location.trackParts[b].type == TrackPartType.Bumper]
                if len(bumper_a) == 0 and len(bumper_b) == 1:
                    if location.trackParts[bumper_b[0]].aSide:
                        gateway = location.trackParts[location.trackParts[bumper_b[0]].aSide[0]]
                    elif location.trackParts[bumper_b[0]].bSide:
                        gateway = location.trackParts[location.trackParts[bumper_b[0]].bSide[0]]
                    if gateway.type == TrackPartType.RailRoad and not gateway.stationPlatform and gateway.id not in facilities and gateway.sawMovementAllowed and gateway.parkingAllowed and gateway.length > 0:
                        gateways.append((gateway, location.trackParts[bumper_b[0]]))
                        logging.info(f"Found gateway track {gateway.name}")
                elif len(bumper_a) == 1 and len(bumper_b) == 0:
                    if location.trackParts[bumper_a[0]].aSide:
                        gateway = location.trackParts[location.trackParts[bumper_a[0]].aSide[0]]
                    elif location.trackParts[bumper_a[0]].bSide:
                        gateway = location.trackParts[location.trackParts[bumper_a[0]].bSide[0]]
                    if gateway.type == TrackPartType.RailRoad and not gateway.stationPlatform and gateway.id not in facilities and gateway.sawMovementAllowed and gateway.parkingAllowed  and gateway.length > 0:
                        gateways.append((gateway, location.trackParts[bumper_a[0]]))
                        logging.info(f"Found gateway track {gateway.name}")
        return gateways

    def generate_train_compositions(self, config, scenario_generator):
        distribution_config = None
        number_train_units = 0
        if "train_unit_distribution" in config:
            # If a specific sublist of train unit types was provided, update the possible train unit types
            if "train_unit_types" in config["train_unit_distribution"]:
                scenario_generator.scenario_TrainUnitTypes = [u for u in scenario_generator.scenario_TrainUnitTypes if u.displayName in config["train_unit_distribution"]["train_unit_types"]]
                self.train_unit_types = scenario_generator.scenario_TrainUnitTypes.copy()
                self.train_units_subtypes = {u.displayName.split("-")[0]: [sub.displayName for sub in self.train_unit_types if u.displayName.split("-")[0] in sub.displayName] for u in self.train_unit_types}
            # If a distribution of train units over the trains was given, use this for the train creation
            distribution_config = config["train_unit_distribution"]
            # type_ratio and number_units_per_train are mandatory parts of the distribution
            distribution_config["number_units_per_train"] = [distribution_config["units_per_composition"][i % len(distribution_config["units_per_composition"])] for i in range(config["number_of_trains"])]
            random.shuffle(distribution_config["number_units_per_train"])
            # This sets the number of different train super types used
            different_types = min(len(self.train_units_subtypes), math.floor(config["number_of_trains"] * distribution_config["super_type_ratio"]) + 1)
            # This is an array with for each train the supertype it will be assigned to
            distribution_config["train_super_types"] = [range(different_types)[i % different_types] for i in range(config["number_of_trains"])]
            random.shuffle(distribution_config["train_super_types"])

            # For each unit subtype we calculate the number of associated train units
            distribution_config["units_per_super_type"] = {t: sum([units for i, units in enumerate(distribution_config["number_units_per_train"]) if distribution_config["train_super_types"][i] == t]) for t in range(different_types)}
            super_types = list(self.train_units_subtypes.keys())

            # For each train, randomly sample the subtype for each unit from the supertype assigned to this train for the known number of units
            distribution_config["subtypes_per_train"] = [[random.choice(self.train_units_subtypes[super_types[t]]) for _ in range(distribution_config["number_units_per_train"][j])] for j, t in enumerate(distribution_config["train_super_types"])]
            # Calculate the number of units per subtype
            distribution_config["number_subtype_units"] = {sub: sum([1 for train in distribution_config["subtypes_per_train"] for u in train if u == sub]) for sub in set([u for train in distribution_config["subtypes_per_train"] for u in train])}
            # This is an array of all the train units, where each item is the subtype of the unit
            distribution_config["unit_types"] = [u for train in distribution_config["subtypes_per_train"] for u in train]
            number_train_units = len(distribution_config["unit_types"])
        elif config["use_default_material"]:
            # For each train to be generated, randomly sample its type and give it a random number of units between 1 and 3 (upper limit not included in randrange)
            distribution_config = {"unit_types_per_train": [(random.choice(self.train_unit_types), random.randrange(1, 4, 1)) for _ in range(config["number_of_trains"])]}
        else:
            # For each train to be generated, randomly sample its type and give it a random number of units between 1 and 3 (upper limit not included in randrange)
            distribution_config = {"random_unit_types_per_train": [(random.choice(self.train_unit_types), random.randrange(1, 4, 1)) for _ in range(config["number_of_trains"])]}
            number_train_units = sum([num for _, num in distribution_config["random_unit_types_per_train"]])
        self.generate_train_units(number_train_units, config["perform_servicing"], distribution_config)
        self.generate_trains(config["number_of_trains"], distribution_config)

        
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

    def generate_train_units(self, number_train_units, servicing, distribution_config = None):
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
                    for typ, num in distribution_config["random_unit_types_per_train"]:
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

    def generate_trains(self, num: int, distribution_config = None):
        distribution = self.distribute_train_units(num, distribution_config)
        for (i, train_units) in enumerate(distribution):
            ### Incoming train
            gateway, side = random.choice(self.gateways["arrival"])
            # Arrive in 2/3 of total time
            start_time = random.randrange(self.scenario_generator.scenario.startTime, self.scenario_generator.scenario.endTime * 2 / 3)
            # Minimum time in yard is 10 minutes + total servicing time
            # TODO servicing time
            end_time = random.randrange(start_time + 600, self.scenario_generator.scenario.endTime)
            train_in = self.scenario_generator.create_Train(
                id=str(i),
                time=start_time,
                members=train_units,
                standingIndex=1, # assume
                sideTrackPart=side.id,
                trackPart=gateway.id,
                canDepartFromAnyTrack=False, # assume
            )
            self.trains.append(train_in)
            self.scenario_generator.add_incomingTrain(train_in)

            ### Outgoing train
            # TODO matching
            gateway, side = random.choice(self.gateways["departure"])
            unmatched_train_units = [self.scenario_generator.create_TrainUnitUnmatchedMembers(train_unit.typeDisplayName) for train_unit in train_units]
            train_out = self.scenario_generator.create_Train(
                id=f"{i+num}",
                time=end_time,
                members=unmatched_train_units,
                standingIndex=1, # assume
                sideTrackPart=side.id,
                trackPart=gateway.id,
                canDepartFromAnyTrack=False, # assume
            )
            self.trains.append(train_out)
            self.scenario_generator.add_outgoingTrain(train_out)


    def distribute_train_units(self, number_trains, distribution_config):
        if self.number_of_train_units < number_trains or self.number_of_train_units > 3 * number_trains:
            raise ValueError(f"Cannot make sure that all {number_trains} trains get between 1 and 3 train units from {len(self.train_units)} units.")

        trains = [[] for _ in range(number_trains)]

        units = self.train_units.copy()
        for typ in units:
            random.shuffle(units[typ])

        if "random_unit_types_per_train" in distribution_config:
            # For each train of a certain type, randomly select the train units part of this train for the predetermined number of units
            for i, (t, num) in enumerate(distribution_config["random_unit_types_per_train"]):
                for _ in range(num):
                    trains[i].append(units[t.displayName].pop())
        elif "number_units_per_train" in distribution_config:
            # The number of units per train and its train type were already generated, so allocate the units.
            # This is the only method that allows train units of same supertype in one composition
            for train_num, sub_type_list in enumerate(distribution_config["subtypes_per_train"]):
                for sub_type in sub_type_list:
                    trains[train_num].append(units[sub_type].pop())
        else:
            # Without any prior knowledge, randomly distribute, though this is prone to vulnerabilities. 
            # Select number of trains per type
            for typ in units:
                number_trains_of_type = random.randint(math.ceil(len(units[typ]) / 3), math.floor(number_trains / len(units)))
                for _ in range(number_trains_of_type):
                    trains.append([units[typ].pop()])

            for unit_type in units:
                trains_of_type = {i: t for i, t in enumerate(trains) if t[0].typeDisplayName == unit_type}
                while units[unit_type]:
                    idx = random.randint(0, len(trains_of_type) - 1)
                    if len(trains_of_type[idx]) < 3 :
                        trains[idx].append(units[unit_type].pop())
        return trains
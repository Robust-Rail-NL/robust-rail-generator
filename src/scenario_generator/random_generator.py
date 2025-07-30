import math
import random
from itertools import product

from Location_pb2 import TrackPartType

class RandomGenerator:
    def __init__(self, gen, seed, location):
        """Initialize the random generator for a specific scenario generator."""
        print("LOG: | Random Generator has been initialized. |")
        self.scenario_generator = gen
        self.seed = seed
        random.seed(self.seed)
        self.train_unit_types = []
        self.train_units = {}
        self.number_of_train_units = 0
        self.trains = []
        self.gateways = self.get_gateway_tracks(location)

    def get_gateway_tracks(self, location):
        gateways = []
        facilities = [t for f in location.facilities for t in f.relatedTrackParts]
        for track in location.trackParts:
            if track.type == TrackPartType.RailRoad:
                bumper_a = [location.trackParts[a].id 
                            for a in track.aSide 
                            if location.trackParts[a].type == TrackPartType.Bumper]
                bumper_b = [location.trackParts[a].id 
                            for a in track.bSide 
                            if location.trackParts[a].type == TrackPartType.Bumper]
                
                if len(bumper_a) == 0 and len(bumper_b) == 1: 
                    if location.trackParts[bumper_b[0]].aSide:
                        gateway = location.trackParts[location.trackParts[bumper_b[0]].aSide[0]]
                    elif location.trackParts[bumper_b[0]].bSide:
                        gateway = location.trackParts[location.trackParts[bumper_b[0]].bSide[0]]
                    
                    if gateway.type == TrackPartType.RailRoad and not gateway.sawMovementAllowed and not gateway.parkingAllowed and not gateway.stationPlatform and gateway.id not in facilities:
                        gateways.append((gateway, location.trackParts[bumper_b[0]]))
                        print(f"Found gateway track {gateway.name}")
                elif len(bumper_a) == 1 and len(bumper_b) == 0: 
                    if location.trackParts[bumper_a[0]].aSide:
                        gateway = location.trackParts[location.trackParts[bumper_a[0]].aSide[0]]
                    elif location.trackParts[bumper_a[0]].bSide:
                        gateway = location.trackParts[location.trackParts[bumper_a[0]].bSide[0]]
                    if gateway.type == TrackPartType.RailRoad and not gateway.sawMovementAllowed and not gateway.parkingAllowed and not gateway.stationPlatform and gateway.id not in facilities:
                        gateways.append((gateway, location.trackParts[bumper_a[0]]))
                        print(f"Found gateway track {gateway.name}") 
                        
                # if len(bumper_a) == 0 and len(bumper_b) == 1:
                #     gateway = location.trackParts[location.trackParts[bumper_b[0]].aSide[0]]
                #     if gateway.type == TrackPartType.RailRoad and not gateway.sawMovementAllowed and not gateway.parkingAllowed and not gateway.stationPlatform and gateway.id not in facilities:
                #         print(f"Found gateway track {gateway.name}")
                #         gateways.append((gateway, location.trackParts[bumper_b[0]]))
        return gateways

    def generate_train_compositions(self, config, scenario_generator):
        distribution_config = None
        number_train_units = 0
        # TODO allow subtypes in same train composition
        if "train_unit_distribution" in config:
            # If a specific sublist of train unit types was provided, update the possible train unit types
            if "train_unit_types" in config["train_unit_distribution"]:
                scenario_generator.scenario_TrainUnitTypes = [u for u in scenario_generator.scenario_TrainUnitTypes if u.displayName in config["train_unit_distribution"]["train_unit_types"]]
                self.train_unit_types = scenario_generator.scenario_TrainUnitTypes.copy()
            # If a distribution of train units over the trains was given, use this for the train creation
            if "train_unit_distribution" in config:
                distribution_config = config["train_unit_distribution"]
                # type_ratio and number_units_per_train are mandatory parts of the distribution
                distribution_config["number_units_per_train"] = [distribution_config["units_per_composition"][i % len(distribution_config["units_per_composition"])] for i in range(config["number_of_trains"])]
                random.shuffle(distribution_config["number_units_per_train"])
                # this sets the number of the train type
                different_types = min(len(distribution_config["train_unit_types"]), math.floor(config["number_of_trains"] * distribution_config["type_ratio"]) + 1)
                distribution_config["train_types"] = [range(different_types)[i % different_types] for i in range(config["number_of_trains"])]
                random.shuffle(distribution_config["train_types"])
                distribution_config["units_per_type"] = {t: sum([units for i, units in enumerate(distribution_config["number_units_per_train"]) if distribution_config["train_types"][i] == t]) for t in range(different_types)}
                distribution_config["unit_types"] = [t for t, num in distribution_config["units_per_type"].items() for _ in range(num)]
                number_train_units = len(distribution_config["unit_types"])
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
                print("WARNING: no distribution config provided, number of train units cannot be simply distributed over number of trains")
            else:
                if "unit_types" in distribution_config:
                    unit_type = distribution_config["train_unit_types"][distribution_config["unit_types"][i]]
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
            print(f"ERROR: expected {number_train_units} train units and {self.number_of_train_units} were created")

    def generate_trains(self, num: int, distribution_config = None):
        distribution = self.distribute_train_units(num, distribution_config)
        for (i, train_units) in enumerate(distribution):
            ### Incoming train
            gateway, side = random.choice(self.gateways)
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
            gateway, side = random.choice(self.gateways)
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
            for i, t in enumerate(distribution_config["train_types"]):
                typ = distribution_config["train_unit_types"][t]
                for _ in range(distribution_config["number_units_per_train"][i]):
                    trains[i].append(units[typ].pop())
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

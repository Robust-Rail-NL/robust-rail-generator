import os
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", help="Location name of location file to reformat (default='kleineBinckhorstNS')", default="kleineBinckhorstNS", required=False)
parser.add_argument("-o", "--output", help="Filename to output to (default=kleineBinckhorst)", default="kleineBinckhorst", required=False)
parser.add_argument("-s", "--station_platforms", help="Whether to include station platform fields (default=False)", default="False", required=False)

def reformat(file, output, station_platforms):
    if "location_" not in file:
        file = f"location_{file}"
    if ".json" in file:
        file = file.replace(".json", "")
    json_obj = json.load(open(os.path.join(os.path.dirname(__file__), f"{file}.json"), "r"))
    location_json = {"trackParts": [], "facilities": []}
    track_parts = update_file_no_empty_neighbor_TrackParts(json_obj["infrastructures"])
    track_names_to_id = {}
    # Store objects which are aside (bside) of a track, so they can be easily retrieved when making objects
    aside_of = {}
    bside_of = {}
    for id, track in enumerate(track_parts):
        track_names_to_id[track['name']] = id
        track_parts[id]["id"] = str(id)
        if "track" in track:
            aside_of[track["track"]["aName"]] = track["name"]
            bside_of[track["track"]["bName"]] = track["name"]
    for track in track_parts:
        # Fourway switches (intersections)
        if "Engels" in track["name"] or "Kruis" in track["name"]:
            location_json["trackParts"].append({
                "id": track["id"],
                "name": track["name"],
                "aSide": [track_names_to_id[track["fourWayConnection"]["aLeftName"]], track_names_to_id[track["fourWayConnection"]["aRightName"]]],
                "bSide": [track_names_to_id[track["fourWayConnection"]["bLeftName"]], track_names_to_id[track["fourWayConnection"]["bRightName"]]],
                "length": 0,
                "sawMovementAllowed": False,
                "parkingAllowed": False,
                "isElectrified": track["isElectrified"],
                "type": "EnglishSwitch" if "Engels" in track["name"] else "Intersection"
            })
            if station_platforms:
                location_json["trackParts"][-1]["stationPlatform"] = False
        # Connection track parts
        elif "_" in track["name"]:
            location_json["trackParts"].append({
                "id": track["id"],
                "name": track["name"],
                "aSide": [track_names_to_id[track["track"]["aName"]]],
                "bSide": [track_names_to_id[track["track"]["bName"]]],
                "length": track["track"]["length"],
                "sawMovementAllowed": track["track"]["reversalAllowed"],
                "parkingAllowed": track["track"]["parkingAllowed"],
                "isElectrified": track["isElectrified"],
                "type": "RailRoad"
            })
            if station_platforms:
                location_json["trackParts"][-1]["stationPlatform"] = False
        # Threeway switches
        elif "Wissel" in track["name"]:
            if track["name"] in aside_of:
                location_json["trackParts"].append({
                    "id": track["id"],
                    "name": track["name"],
                    "aSide": [track_names_to_id[track["switch"]["leftName"]], track_names_to_id[track["switch"]["rightName"]]],
                    "bSide": [track_names_to_id[track["switch"]["permanentName"]]],
                    "length": 0,
                    "sawMovementAllowed": False,
                    "parkingAllowed": False,
                    "isElectrified": track["isElectrified"],
                    "type": "Switch"
                })
                if station_platforms:
                    location_json["trackParts"][-1]["stationPlatform"] = False
            elif track["name"] in bside_of:
                location_json["trackParts"].append({
                    "id": track["id"],
                    "name": track["name"],
                    "aSide": [track_names_to_id[track["switch"]["permanentName"]]],
                    "bSide": [track_names_to_id[track["switch"]["leftName"]], track_names_to_id[track["switch"]["rightName"]]],
                    "length": 0,
                    "sawMovementAllowed": False,
                    "parkingAllowed": False,
                    "isElectrified": track["isElectrified"],
                    "type": "Switch"
                })
                if station_platforms:
                    location_json["trackParts"][-1]["stationPlatform"] = False
        # End of tracks
        elif "sein" in track["name"].lower() or "stootblok" in track["name"].lower():
            location_json["trackParts"].append({
                "id": track["id"],
                "name": track["name"],
                "aSide": [track_names_to_id[bside_of[track["name"]]]] if track["name"] in bside_of else [],
                "bSide": [track_names_to_id[aside_of[track["name"]]]] if track["name"] in aside_of else [],
                "length": 0,
                "sawMovementAllowed": False,
                "parkingAllowed": False,
                "isElectrified": track["isElectrified"],
                "type": "Bumper"
            })
            if station_platforms:
                location_json["trackParts"][-1]["stationPlatform"] = False
        # Regular tracks
        else:
            location_json["trackParts"].append({
                "id": track["id"],
                "name": track["name"],
                "aSide": [track_names_to_id[track["track"]["aName"]]],
                "bSide": [track_names_to_id[track["track"]["bName"]]],
                "length": track["track"]["length"],
                "sawMovementAllowed": track["track"]["reversalAllowed"],
                "parkingAllowed": track["track"]["parkingAllowed"],
                "isElectrified": track["isElectrified"],
                "type": "RailRoad"
            })
            if station_platforms:
                location_json["trackParts"][-1]["stationPlatform"] = track["track"]["stationPlatform"] if "stationPlatform" in track["track"] else False
    for i, facility in enumerate(json_obj["facilities"]):
        location_json["facilities"].append({
            "id": str(i+len(track_names_to_id)),
            "type": facility["name"],
            "relatedTrackParts": [track_names_to_id[t] for t in facility["relatedInfrastructureNames"]]
        })
    json.dump(location_json, open(os.path.join(os.path.dirname(__file__), f"location_{output}.json"), "w"), indent=4)


def update_file_no_empty_neighbor_TrackParts(track_parts):
    ### We don't include the FT track parts, so update the ids
    missing_ids = []
    names_to_ids = {}
    for track in track_parts:
        names_to_ids[track["name"]] = int(track["id"])
        track["id"] = int(track["id"])
        if "FT" in track["name"]:
            missing_ids.append(track["id"])
    updated_ids = {}
    for id in missing_ids:
        for i in range(int(id)+1, len(track_parts)):
            track_parts[i]["id"] -= 1
            updated_ids[track_parts[i]["name"]] = track_parts[i]["id"]
    new_track_parts = []
    for track in track_parts:
        if "FT" not in track["name"]:
            new_track_parts.append(track)
    return new_track_parts



if __name__ == "__main__":
    args = parser.parse_args()
    reformat(args.file, args.output, args.station_platforms.lower() == "true")




# The kleineBinckhorstNS file has 906c instead of 906b, which end at a bumper, while switch 425 is connected to signal 436, and that track end there. 

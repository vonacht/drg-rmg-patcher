import json
import copy
import argparse
import logging

from uassetgen import JSON_to_uasset

DEFAULT_ROOMS_PATH = "/Game/Maps/Rooms/RoomGenerators/"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

def find_import_idx(import_list, room):
    for ii, obj in enumerate(import_list):
        if obj["ObjectName"] == room:
            return -(ii+1)
    return None


def main():

    parser = argparse.ArgumentParser(
        description="Patcher for DRG's RMG_ExtractionLinear file. Used to add custom rooms or remove existing rooms."
    )
    parser.add_argument(
        "-c",
        "--config_path",
        nargs="?",
        default="config/config.json",
        help="Path to the user configuration file. If not defined defaults to config/config.json.",
    )
    parser.add_argument(
        "-o",
        "--output_path",
        nargs="?",
        default="cache/RMG_ExtractionLinear_patched.uasset",
        help="Path where the patched RMG file will be written. If not specified defaults to cache/",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Writes the patched UAsset in JSON form together with the output in the cache/ directory.",
    )
    args = parser.parse_args()

    # Getting the necessary data from the default file:
    with open("assets/RMG_ExtractionLinear.json", "r") as f:
        original_rmg = json.load(f)
    export_length = len(original_rmg["Exports"][0]["Data"][0]["Value"])
    default_export_entry = original_rmg["Exports"][0]["Data"][0]["Value"][0]
    import_length = len(original_rmg["Imports"])
    default_import = original_rmg["Imports"][0]

    # Getting the user configuration file with the rooms to be added/removed:
    try:
        with open(args.config_path, "r") as f:
            user_config_file = json.load(f)
        logging.info(f"Opening user configuration file: {args.config_path}")
    except OSError as e:
        logging.error(f"Error opening {args.config_path}: {e}")
        return 1

    ## TODO: add jsonschema validation

    patched_json = copy.deepcopy(original_rmg)
    if user_config_file["Add"]:
        for ii, room_to_add in enumerate(user_config_file["Add"]):
            # 1. Patch the imports:
            room_path = DEFAULT_ROOMS_PATH + room_to_add
            package_import = copy.deepcopy(default_import)
            package_import.update(
                {"ObjectName": room_path, "OuterIndex": 0, "ClassName": "Package"}
            )
            patched_json["Imports"].append(package_import)
            room_import = copy.deepcopy(default_import)
            room_import.update(
                {
                    "ObjectName": room_to_add,
                    "OuterIndex": -(import_length + 1 + 2 * ii),
                    "ClassName": "RoomGenerator",
                    "ClassPackage": "/Script/FSD"
                }
            )
            patched_json["Imports"].append(room_import)
            # 2. Patch the exports:
            room_export = copy.deepcopy(default_export_entry)
            room_export.update(
                {"Name": f"{ii + export_length}", "Value": -(import_length + 2 + 2 * ii)}
            )
            patched_json["Exports"][0]["Data"][0]["Value"].append(room_export)
            patched_json["Exports"][0]["CreateBeforeSerializationDependencies"].append(-(import_length + 2 + 2*ii))
            # 3. Patch the NameMap:
            patched_json["NameMap"].extend([room_path, room_to_add])
            logging.info(f"Added room {room_to_add}.")
    else:
        logging.info("No room to add found in config file. Skipping.")

    if user_config_file["Remove"]:
        for room_to_remove in user_config_file["Remove"]:
            room_idx = find_import_idx(original_rmg["Imports"], room_to_remove)
            if room_idx is None:
                logging.info(f"Room to remove {room_to_remove} no found in file. Skipping.")
                continue
            else:
                exports = copy.deepcopy(patched_json["Exports"])
                exports[0]["Data"][0]["Value"] = [exp for exp in exports[0]["Data"][0]["Value"] if exp["Value"] != room_idx]
                patched_json["Exports"] = exports
                logging.info(f"Removed room {room_to_remove}.")
    else:
        logging.info("No room to remove found in config file. Skipping.")

    if user_config_file["Add"] or user_config_file["Remove"]:
        if args.debug:
            with open("cache/json_debug.json", "w") as f:
                json.dump(patched_json, f, indent=4)
            logging.info("Writing debug JSON in cache/json_debug.json")
        try:
            JSON_to_uasset(patched_json, args.output_path)
        except Exception as e:
            logging.error(f"Error when writing the patched UAsset: {e}")
    else:
        logging.info("Config file empty. Finishing.")

if __name__ == "__main__":
    main()

import json
import copy
import argparse
import logging

from uassetgen import JSON_to_uasset

DEFAULT_ROOMS_PATH = "/Game/Maps/Rooms/RoomGenerators/"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


def main():

    parser = argparse.ArgumentParser(
        description="Example CLI with a positional argument"
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
        help="Path where the patched RMG file will be written.",
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
    with open("assets/test.json", "w") as f:
        json.dump(patched_json, f, indent=4)
    try:
        JSON_to_uasset(patched_json, args.output_path)
    except Exception as e:
        logging.error(f"Error when writing the patched UAsset: {e}")


if __name__ == "__main__":
    main()

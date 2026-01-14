from pythonnet import load
import logging

load("coreclr")
import clr
import json
from pathlib import Path


def JSON_to_uasset(
    input_json: dict, output_path: str = "cache/RMG_ExtractionLinear_patched.uasset"
):
    # Load the assembly. The dll_path needs to be an absolute reference to libs/UAssetAPI.dll:
    dll_path = Path.cwd() / "libs" / "UAssetAPI.dll"
    clr.AddReference(str(dll_path))
    # We load the methods to read from JSON and save:
    from UAssetAPI import UAsset
    from UAssetAPI import UnrealTypes

    # DeserializeJson expects a string:
    UAsset.DeserializeJson(json.dumps(input_json)).Write(
            output_path
    )
    logging.info(f"Writing the patched UAsset in {output_path}")
    

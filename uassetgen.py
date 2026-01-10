from pythonnet import load
import logging

load("coreclr")
import clr
import json
import os


def JSON_to_uasset(
    input_json: dict, output_path: str = "cache/RMG_ExtractionLinear_patched.uasset"
):
    dll_path = os.environ["UASSETAPI_DLL_PATH"]
    # Load the assembly:
    clr.AddReference(f"{dll_path}/libs/UAssetAPI.dll")
    # We load the methods to read from JSON and save:
    from UAssetAPI import UAsset
    from UAssetAPI import UnrealTypes

    # DeserializeJson expects a string:
    UAsset.DeserializeJson(json.dumps(input_json)).Write(
        f"cache/RMG_ExtractionLinear_patched_pre.uasset"
    )
    json_string = UAsset(
        f"cache/RMG_ExtractionLinear_patched_pre.uasset",
        UnrealTypes.EngineVersion.VER_UE4_27,
    ).SerializeJson()
    UAsset.DeserializeJson(json_string).Write(output_path)
    logging.info(f"Writing the patched UAsset in {output_path}")

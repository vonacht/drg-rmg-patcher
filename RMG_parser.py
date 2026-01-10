import json

with open("assets/RMG_ExtractionLinear.json", "r") as f:
    original_rmg = json.load(f)

room_paths = [
    path["ObjectName"]
    for path in original_rmg["Imports"]
    if path["ClassName"] == "Package"
]
rooms = [
    path["ObjectName"]
    for path in original_rmg["Imports"]
    if path["ClassName"] == "RoomGenerator"
]

print(len(rooms))

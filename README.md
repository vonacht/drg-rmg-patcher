This is a simple Python script that creates a patched RMG file for Deep Rock Galactic. The RMG file contains the available pool of rooms when generating the procedural maps. The script allows to add new rooms (see https://github.com/vonacht/drg-room-editor/) or to remove existing rooms.

The script uses uv to manage the dependencies. The rooms to be added or removed are specified in a JSON file inside config:

```json
#config/config.json
{
    "Add": ["RMA_Custom01", "RMA_Custom02"],
    "Remove": ["RMA_Tiny_Slopes01"]
}
```

After editing the config, you can run the script with:

`uv run main.py`

The patched RMG file will be placed in the cache/ directory. A different config file can be provided with option -c:

`uv run main.py -c myconfigfile.json`

and a different output path for the patched UAsset can be specified with option -o:

`uv run main.py -o ~/modding/RMG_test/RMG_ExtractionLinear.uasset`



# Scripts for Aseprite v1.3-beta (tilemap editor)

These Lua scripts automate Tileset and Tilemap import/export.

Both ```Export Tilemap.lua``` and ```Export Tileset.lua``` are modified versions of scripts by [David Capello](https://github.com/dacap).
```Export IndexedImage.lua``` is modified from the [GameboyExport](https://github.com/boombuler/aseprite-gbexport) script by boombuler. 
Credit to [rxi](https://github.com/rxi/json.lua) for ```json.lua```.
Everything including my modifications are under the MIT licence, feel free to use and modify.

- ```Export Tilemap.lua``` uses json.lua to export aseprite tile indices for each tilemap layer. The exported active area is visible in aseprite by holding the ctrl key. Let me repeat: Exported tilemaps are *NOT* for the whole canvas. I don't know how to change this behavior. 

- ```Export Tileset.lua``` exports the tileset into a rectangular ```png``` with a maximal ```row_len```. The script uses the tileset that results from copying and flattening all layers of every frame. I use it to create animated tiles that have different backgrounds.

- ```Import Tileset.lua``` uses layer names of all tilemap layers to import tilesets. For each tilemap layer, a new tilemap layer is created, the tileset is imported from the ```Tileset_*layer_name*.png``` file, then the pixels from the old tilemap layers are copied over. This operation is repeated for every frames. Finally, the old tilemap layers are discarded and the new ones renamed to their respective names.

- ```Import Tileset.lua``` uses layer names of all tilemap layers to import tilesets. For each tilemap layer, a new tilemap layer is created, the tileset is imported from the ```Tileset_*layer_name*.png``` file, then the pixels from the old tilemap layers are copied over. This operation is repeated for every frames. Finally, the old tilemap layers are discarded and the new ones renamed to their respective names.

- ```Export IndexedImage.lua``` exports raw indexed image to be used for palette swapping. 

## To Do
- ```Import Tileset.lua``` has trouble importing tilesets to empty layers/cels.



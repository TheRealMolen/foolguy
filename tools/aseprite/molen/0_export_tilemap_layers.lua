-- export all tilemap layers as PNGs
-- ignore any with '_exclude' in the name
-- filenames are export/<og-filename-noext>/<layername>.png

local fs = app.fs

local function log(msg)
  --print(msg)
end


-- ensures the output folder is created and returns the path to it (including trailing /)
local function prepare_output_folder()
  local fileName = app.activeSprite.filename
  local filePath = fs.filePath(fileName)

  local exportDir = fs.joinPath(filePath, "export")
  if not fs.isDirectory(exportDir) then
    fs.makeDirectory(exportDir)
  end

  local fileTitle = fs.fileTitle(fileName)
  local outputDir = fs.joinPath(exportDir, fileTitle)
  if not fs.isDirectory(outputDir) then
    fs.makeDirectory(outputDir)
  end

  return outputDir .. fs.pathSeparator
end


local function hide_all_layers(sprite)
  local initialVis = {}

  for i,layer in ipairs(sprite.layers) do
    initialVis[layer.name] = layer.isVisible
    layer.isVisible = false
  end

  return initialVis
end

local function restore_layer_visibiity(sprite, vis)
  for i,layer in ipairs(sprite.layers) do
    layer.isVisible = vis[layer.name]
  end
end



local function export_layer(sprite, layer, outputDir)
  layer.isVisible = true

  local pngName = string.format("%s.png", layer.name)
  local layerFileName = outputDir .. pngName

  log("exporting layer '" .. layer.name .. "'" .. " to '" .. layerFileName .. "'")
  sprite:saveCopyAs(layerFileName)

  layer.isVisible = false

  return pngName
end


-- main entry point
local function export_layers()
  log("go go gadget exporter")

  local outputDir = prepare_output_folder()
  if not outputDir then
    return
  end
  log("export folder: " .. outputDir)

  local sprite = app.activeSprite

  local initialVis = hide_all_layers(sprite)
  local pngList = ""

  for i,layer in ipairs(sprite.layers) do

    if layer.isTilemap and not layer.isBackground then

      if not string.find(layer.name, "_exclude") then
        local pngName = export_layer(sprite, layer, outputDir)
        pngList = pngList .. " " .. pngName
      end
    end
  end

  local manifestName = outputDir .. "manifest.txt"
  local file = io.open(manifestName, "w")
  file:write(pngList)
  file:close()

  restore_layer_visibiity(sprite, initialVis)
end


app.transaction(
  "Export All Layers",
  function()
    export_layers()
  end
)


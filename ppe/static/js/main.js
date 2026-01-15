import proj4 from "proj4";
import Map from "ol/Map.js";
import View from "ol/View";
import { ImageWMS, WMTS } from "ol/source";
import { Image as ImageLayer, Tile as TileLayer } from "ol/layer";
import { Projection } from "ol/proj";
import { register } from "ol/proj/proj4";
import WMTSTileGrid from "ol/tilegrid/WMTS";

import "./style.css";

const crs = "EPSG:2056";
const extent = [2420000, 1030000, 2900000, 1360000];

proj4.defs(
  crs,
  "+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 +x_0=2600000" +
    " +y_0=1200000 +ellps=bessel +towgs84=674.374,15.056,405.346,0,0,0,0 +units=m +no_defs",
);
register(proj4);

const projection = new Projection({
  code: crs,
  extent: extent,
});

const resolutions = [
  250, 100, 50, 20, 10, 5, 2.5, 2, 1.5, 1, 0.5, 0.25, 0.125, 0.0625, 0.03125,
  0.015625, 0.0078125,
];

const tileGrid = new WMTSTileGrid({
  origin: [extent[0], extent[3]],
  resolutions,
  matrixIds: resolutions.map((_, i) => i),
});

const map = new Map({
  target: "map",
  view: new View({
    projection,
    center: [2550000, 1207000],
    resolution: 1,
    resolutions,
    constrainResolution: true,
  }),
});

function createWmtsLayer(layerName, format, label) {
  return new TileLayer({
    visible: false,
    source: new WMTS({
      layer: layerName,
      crossOrigin: "anonymous",
      attributions: '<a target="new" href="https://www.ne.ch/sitn">SITN</a>',
      projection,
      url: `https://sitn.ne.ch/services/wmts/1.0.0/{layer}/{style}/{TileMatrixSet}/{TileMatrix}/{TileRow}/{TileCol}.${format}`,
      tileGrid,
      matrixSet: "EPSG2056",
      style: "default",
      requestEncoding: "REST",
    }),
    properties: {
      label,
      layerName,
    },
  });
}

const backgroundLayers = [
  createWmtsLayer("ortho2022", "jpeg", "Orthophoto"),
  createWmtsLayer("plan_ville_toits_gris", "png", "Plan de ville"),
  createWmtsLayer("plan_cadastral", "png", "Plan cadastral"),
];

const layerSelectEl = document.getElementById("background-selector");
backgroundLayers[0].setVisible(true);
backgroundLayers.forEach((layer) => {
  const optionEl = document.createElement("option");
  optionEl.value = layer.get("layerName");
  optionEl.innerHTML = layer.get("label");
  layerSelectEl.appendChild(optionEl);
  map.addLayer(layer);
});

layerSelectEl.onchange = () =>
  backgroundLayers.forEach((layer) =>
    layer.setVisible(layer.get("layerName") === layerSelectEl.value),
  );

const wmsLayer = new ImageLayer({
  extent,
  source: new ImageWMS({
    url: "https://sitn.ne.ch/services/wms",
    params: {
      LAYERS:
        "at034_autorisation_construire_pendant,at034_autorisation_construire_apres",
    },
    serverType: "mapserver",
  }),
});

map.addLayer(wmsLayer);

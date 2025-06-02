lizMap.events.on({
  'layersadded': function addCustomLayers(map) {
    const extent = [-20037508.34, -20037508.34, 20037508.34, 20037508.34];

    const tileLayer = new ol.layer.Tile({
      source: new ol.source.XYZ({
        url: 'https://htonl.dev.openstreetmap.org/ngi-tiles/tiles/50k/{z}/{x}/{-y}.png',
        tileGrid: ol.tilegrid.createXYZ({
          extent: extent,
          tileSize: 256,
          minZoom: 0,
          maxZoom: 15
        }),
        projection: 'EPSG:3857'
      })
    });

    map.addLayer(tileLayer);
  }
});

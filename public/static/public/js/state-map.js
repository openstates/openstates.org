import mapboxgl from 'mapbox-gl'
import stateBounds from './state-bounds'
import config from './config'

export default (container) => {
  mapboxgl.accessToken = config.MAPBOX_ACCESS_TOKEN

  const state = container.getAttribute('data-value')

  const map = new mapboxgl.Map({
    container,
    style: config.MAP_BASE_STYLE,
    interactive: true,
    // These are the min and max zooms at which the SLD map tiles exist
    minZoom: 2,
    maxZoom: 13
  });

  map.fitBounds(stateBounds[state], 
    { padding: 25, animate: false }
  );

    map.on('load', function () {
        // const districtType = districtId.includes('sldu') ? 'sldu' : 'sldl'
        const outline = {...config.MAP_DISTRICTS_OUTLINE, filter: ['==', 'state', state]};
        map.addLayer(outline);
        const fill = {...config.MAP_DISTRICTS_FILL, filter: ['==', 'state', state]};
        map.addLayer(fill);
        const stroke = {...config.MAP_DISTRICTS_STROKE, filter: ['==', 'state', state]}
        map.addLayer(stroke);
    })
}

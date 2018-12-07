import mapboxgl from 'mapbox-gl'

import stateBounds from './state-bounds'

export default () => {
  mapboxgl.accessToken = 'pk.eyJ1Ijoib3BlbnN0YXRlcyIsImEiOiJjamU2NmJ2dmsxdTFzMzRycTNhejNjdTUzIn0.QHziTq0NGFutvZzo9Wmc0w'

  const container = document.querySelector('[data-hook="legislator-map"]')
  const districtId = container.getAttribute('data-value')

  const map = new mapboxgl.Map({
    container,
    style: 'mapbox://styles/mapbox/light-v9',
    interactive: false,
    // These are the min and max zooms at which the SLD map tiles exist
    minZoom: 2,
    maxZoom: 13
  });

  fetch('https://data.openstates.org/boundaries/2018/' + districtId + '.json')
    .then(function(response) {
        return response.json();
    }).then(function(json) {
        console.log(json.extent);
        map.fitBounds(json.extent, 
            { padding: 25, animate: false }
        );
    });

  map.on('load', function () {
    const districtType = districtId.includes('sldu') ? 'sldu' : 'sldl'

    map.addLayer({
      id: 'other-districts',
      type: 'line',
      source: {
        type: 'vector',
        url: 'mapbox://openstates.sld'
      },
      'source-layer': 'sld',
      paint: {
        'line-color': 'black',
        'line-opacity': 0.4,
        'line-width': 1.0
      },
    })

    map.addLayer({
      id: 'district-fill',
      type: 'fill',
      source: {
        type: 'vector',
        url: 'mapbox://openstates.sld'
      },
      'source-layer': 'sld',
      paint: {
        'fill-color': 'green',
        'fill-opacity': 0.2
      },
      filter: ['==', 'ocdid', districtId]
    })

    map.addLayer({
      id: 'district-stroke',
      type: 'line',
      source: {
        type: 'vector',
        url: 'mapbox://openstates.sld'
      },
      'source-layer': 'sld',
      paint: {
        'line-color': 'green',
        'line-opacity': 0.4,
        'line-width': 1.0
      },
      filter: ['==', 'ocdid', districtId]
    })
  })
}

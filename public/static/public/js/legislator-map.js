import mapboxgl from 'mapbox-gl'

import stateBounds from './state-bounds'

export default () => {
  mapboxgl.accessToken = 'pk.eyJ1Ijoib3BlbnN0YXRlcyIsImEiOiJjamU2NmJ2dmsxdTFzMzRycTNhejNjdTUzIn0.QHziTq0NGFutvZzo9Wmc0w'
  
  const container = document.querySelector('[data-hook="legislator-map"]')
  const districtId = container.getAttribute('data-value')

  // Temporarily use the entire state as the bounds to zoom to
  // Replace this with zooming to the district itself, once that static API is up:
  // https://github.com/openstates/openstates-district-maps/issues/11
  const state = districtId.match(/\/state:([a-z]{2})\//)[1]
  const bounds = stateBounds[state]

  const map = new mapboxgl.Map({
    container,
    style: 'mapbox://styles/mapbox/light-v9',
    interactive: false,
    // These are the min and max zooms at which the SLD map tiles exist
    // https://github.com/openstates/new-openstates.org
    minZoom: 2,
    maxZoom: 13
  }).fitBounds(
    bounds,
    {
      padding: 25,
      animate: false
    }
  )

  map.on('load', function () {
    const districtType = districtId.includes('sldu') ? 'sldu' : 'sldl'

    map.addLayer({
      id: 'sld',
      type: 'line',
      source: {
        type: 'vector', 
        url: 'mapbox://openstates.sld'
      },
      'source-layer': 'sld',
      paint: {
        'line-color': 'green',
        'line-opacity': 0.2,
        'line-width': 1.0
      },
      filter: ['==', 'type', districtType]
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
        'fill-color': 'black',
        'fill-opacity': 0.2,
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
        'line-color': 'black',
        'line-opacity': 0.4,
        'line-width': 2.0
      },
      filter: ['==', 'ocdid', districtId]
    })
  })
}

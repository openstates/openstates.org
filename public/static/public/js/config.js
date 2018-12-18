
export default {
    MAPBOX_ACCESS_TOKEN: 'pk.eyJ1Ijoib3BlbnN0YXRlcyIsImEiOiJjamU2NmJ2dmsxdTFzMzRycTNhejNjdTUzIn0.QHziTq0NGFutvZzo9Wmc0w',
    MAP_BASE_STYLE: 'mapbox://styles/mapbox/light-v9',
    MAP_SLD_SOURCE: 'mapbox://openstates.sld',
    MAP_DISTRICTS_FILL: {
      id: 'district-fill',
      type: 'fill',
      paint: {
          'fill-color': 'green',
          'fill-opacity': 0.2,
      },
    },
    MAP_DISTRICTS_STROKE: {
      id: 'district-stroke',
      type: 'line',
      paint: {
        'line-color': 'green',
        'line-opacity': 0.4,
        'line-width': 1.0
      },
    }
}

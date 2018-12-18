import mapboxgl from 'mapbox-gl'
import config from './config'

export default () => {
  mapboxgl.accessToken = 'pk.eyJ1Ijoib3BlbnN0YXRlcyIsImEiOiJjamU2NmJ2dmsxdTFzMzRycTNhejNjdTUzIn0.QHziTq0NGFutvZzo9Wmc0w'

  const container = document.querySelector('[data-hook="legislator-map"]')
  const districtId = container.getAttribute('data-value')

  const map = new mapboxgl.Map({
    container,
    style: config.MAP_BASE_STYLE,
    interactive: false,
    // These are the min and max zooms at which the SLD map tiles exist
    minZoom: 2,
    maxZoom: 13
  });

  fetch('https://data.openstates.org/boundaries/2018/' + districtId + '.json')
    .then(function(response) {
        if(!response.ok) {
            throw Error(response.status);
        }
        return response.json();
    }).then(function(json) {
        map.fitBounds(json.extent, 
            { padding: 25, animate: false }
        );
    }).catch(function(error) {
        console.log(error);
        container.style.display = "none";
    });

  map.on('load', function () {
    const districtType = districtId.includes('sldu') ? 'sldu' : 'sldl'

    const outline = {...config.MAP_DISTRICTS_OUTLINE};
    map.addLayer(outline);
    const fill = {...config.MAP_DISTRICTS_FILL, filter: ['==', 'ocdid', districtId]};
    map.addLayer(fill);
    const stroke = {...config.MAP_DISTRICTS_STROKE, filter: ['==', 'ocdid', districtId]}
    map.addLayer(stroke);
  })
}

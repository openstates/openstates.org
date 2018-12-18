import React from 'react'
import mapboxgl from 'mapbox-gl'
import ReactMapboxGl, {Source, Layer} from "react-mapbox-gl";
import stateBounds from './state-bounds'
import config from './config'

const Map = ReactMapboxGl({
    accessToken: config.MAPBOX_ACCESS_TOKEN,
});

export default class StateMap extends React.Component {
    render () {
        return (<Map
            style={config.MAP_BASE_STYLE}
            minZoom={2}
            maxZoom={13}
            interactive={true}
            fitBounds={stateBounds[this.props.state]}

        >
            <Source id="sld" tileJsonSource={{type: "vector", url: "mapbox://openstates.sld"}} />
            <Layer
                id={config.MAP_DISTRICTS_FILL.id}
                type={config.MAP_DISTRICTS_FILL.type}
                sourceId="sld"
                sourceLayer="sld"
                paint={config.MAP_DISTRICTS_FILL.paint} />
        </Map>);
    }
}

  // map.fitBounds(stateBounds[state], 
  //   { padding: 25, animate: false }
  // );


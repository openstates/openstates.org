import React from 'react'
import mapboxgl from 'mapbox-gl'
import ReactMapboxGl, {Source, Layer, Feature} from "react-mapbox-gl";
import stateBounds from './state-bounds'
import config from './config'

const Map = ReactMapboxGl({
    accessToken: config.MAPBOX_ACCESS_TOKEN,
});

export default class StateMap extends React.Component {
    constructor (props) {
        super(props);
        this.state = {
            chamberType: 'sldl',
        };
    }

    render () {
        const filter = ["all",
            ["==", "state", this.props.state],
            ["==", "type", this.state.chamberType]
        ];
        return (
            <div style={{height: "100%"}}>
            <Map
                style={config.MAP_BASE_STYLE}
                minZoom={2}
                maxZoom={13}
                interactive={true}
                fitBounds={stateBounds[this.props.state]}
                fitBoundsOptions={{padding: 25, animate: false}}
                containerStyle={{height: "100%", width: "100%" }}
            >
            <Source id="sld" tileJsonSource={{type: "vector", url: config.MAP_SLD_SOURCE}} />
            <Layer
                id={config.MAP_DISTRICTS_FILL.id}
                type={config.MAP_DISTRICTS_FILL.type}
                sourceId="sld"
                sourceLayer="sld"
                paint={config.MAP_DISTRICTS_FILL.paint}
                filter={filter}
            />
            <Layer
                id={config.MAP_DISTRICTS_STROKE.id}
                type={config.MAP_DISTRICTS_STROKE.type}
                sourceId="sld"
                sourceLayer="sld"
                paint={config.MAP_DISTRICTS_STROKE.paint}
                filter={filter}
            />
        </Map>
        <div class="button-group">
            <button className={this.state.chamberType === 'sldl' ? 'button button--active':'button'}
                onClick={() => this.setState({chamberType: "sldl"})}>House</button>
            <button className={this.state.chamberType === 'sldu' ? 'button button--active':'button'}
                onClick={() => this.setState({chamberType: "sldu"})}>Senate</button>
        </div>
        </div>);
    }
}

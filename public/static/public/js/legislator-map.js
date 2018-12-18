import React from 'react'
import ReactMapboxGl, {Source, Layer } from "react-mapbox-gl"
import config from './config'
import stateBounds from './state-bounds.js'

const Map = ReactMapboxGl({
    accessToken: config.MAPBOX_ACCESS_TOKEN,
});

export default class DistrictMap extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            bounds: stateBounds[props.state],
            display: true,
        }
    }

    componentDidMount() {
        const map = this;
        fetch('https://data.openstates.org/boundaries/2018/' + map.props.districtId + '.json')
          .then(function(response) {
              if(!response.ok) {
                  throw Error(response.status);
              }
              return response.json();
          }).then(function(json) {
              map.setState({bounds: json.extent});
          }).catch(function(error) {
              console.log(error);
              //map.setState({display: false});
          });
    }

    render() {
        var districtFilter = null;
        if (this.props.state == "dc") {
            console.log(this.props.districtId);
            districtFilter = ["==", "state", "dc"];
        } else {
            const districtType = this.props.districtId.includes('sldu') ? 'sldu' : 'sldl';
            districtFilter = ["==", "type", districtType];
        }
        const filter = ["all",
            ["==", "ocdid", this.props.districtId],
            districtFilter
        ];
        if (!this.state.display) {
            return null;
        }
        return (
        <Map
            style={config.MAP_BASE_STYLE}
            minZoom={2}
            maxZoom={13}
            interactive={false}
            fitBounds={this.state.bounds}
            fitBoundsOptions={{padding: 25, animate: false}}
            containerStyle={{height: "100%", width: "100%" }}
        >
            <Source id="sld" tileJsonSource={{type: "vector", url: config.MAP_SLD_SOURCE}} />
            <Layer
                id={config.MAP_DISTRICTS_STROKE.id}
                type={config.MAP_DISTRICTS_STROKE.type}
                sourceId="sld"
                sourceLayer="sld"
                paint={config.MAP_DISTRICTS_STROKE.paint}
                filter={districtFilter}
            />
            <Layer
                id={config.MAP_DISTRICTS_FILL.id}
                type={config.MAP_DISTRICTS_FILL.type}
                sourceId="sld"
                sourceLayer="sld"
                paint={config.MAP_DISTRICTS_FILL.paint}
                filter={filter}
            />
        </Map>
        );
    }
}

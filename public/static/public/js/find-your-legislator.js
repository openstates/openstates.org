import React from 'react';
import { withGoogleMap, GoogleMap, Marker, Polygon } from "react-google-maps";
import LegislatorImage from './legislator-image';
import config from "./config";


function multipolyToPath(coordinates) {
    return coordinates.map(polygon =>
        polygon[0].map(point =>
            ({lat: point[1], lng: point[0]})
        )
    )
}

function chamberColor(leg) {
  return (leg.chamber === "lower" ?  config.LOWER_CHAMBER_COLOR : config.UPPER_CHAMBER_COLOR);
}

const Map = withGoogleMap(function(props) {
  var shapes = [];
  for(var leg of props.legislators) {
    if(leg.shape) {
      const color = chamberColor(leg);
      shapes.push(<Polygon key={leg.division_id}
        defaultPaths={multipolyToPath(leg.shape.coordinates)}
        options={{fillColor: color, strokeColor: color, strokeWeight: 2}}
      />);
    }
  }

    return <GoogleMap defaultZoom={props.zoom}
      center={{ lat: props.lat, lng: props.lon }}
      options={{styles: GOOGLE_MAP_STYLES, disableDefaultUI: true}}
    >
        <Marker position={{ lat: props.lat, lng: props.lon }} />
        {shapes}
    </GoogleMap>
});


export default class FindYourLegislator extends React.Component {
    constructor (props) {
        super(props);
        const queryParams = new URLSearchParams(window.location.search);
        this.state = {
            address: queryParams.get("address") || '',
            lat: 0,
            lon: 0,
            legislators: [],
            error: "",
        };
        this.handleAddressChange = this.handleAddressChange.bind(this);
        this.geocode = this.geocode.bind(this);
        this.geolocate = this.geolocate.bind(this);

        if(this.state.address) {
            this.geocode();
        }
    }

    handleAddressChange(event) {
      this.setState({address: event.target.value});
    }

    setError(message) {
        this.setState({
            error: message,
            legislators: [],
            showMap: false
        });
    }

    geolocate() {
        const component = this;
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
            component.setState({
              lat: position.coords.latitude,
              lon: position.coords.longitude
            });
            component.updateLegislators();
          }, function() {
            component.setError("Geolocation was not available, try entering your address.");
          });
        } else {
            component.setError("Geolocation was not available, try entering your address.");
        }
    }

    geocode() {
      const component = this;
      const url = `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURI(this.state.address)}.json?country=US&limit=1&access_token=${config.MAPBOX_ACCESS_TOKEN}`;
      
      fetch(url)
          .then(response => response.json())
        .then(function(json) {
          console.log(json);
            component.setState({
              lat: json.features[0].center[1],
              lon: json.features[0].center[0],
            });
            component.updateLegislators();
          }).catch(function(error) {
            console.error(error);
            component.setError("Unable to geolocate your address, try adding more information.");
          });
    }

    updateLegislators() {
        if(!this.state.lat || !this.state.lon) {
            this.setState({legislators: [], showMap: false});
        } else { 
            const component = this;
            fetch(`/find_your_legislator/?lat=${this.state.lat}&lon=${this.state.lon}`)
                .then(response => response.json())
                .then(function(json) {
                    component.setState({legislators: json.legislators});

                    for(var leg of json.legislators) {
                        fetch(`https://data.openstates.org/boundaries/2018/${leg.division_id}.json`)
                            .then(response => response.json())
                            .then(function(json) {
                                for(var stleg of component.state.legislators) {
                                    if (stleg.division_id === json.division_id) {
                                        stleg.shape = json.shape;
                                    }
                                }
                                component.setState({legislators: component.state.legislators, showMap: true, error: null});
                            });
                    }
                });
        }

    }

    render() {
      const rows = this.state.legislators.map(leg => <tr key={leg.name}>
        <td><LegislatorImage id={leg.id} image={leg.image} /></td>
        <td><a href={leg.pretty_url}>{leg.name}</a></td>
        <td>{leg.party}</td>
        <td>{leg.district}</td>
        <td style={{backgroundColor: chamberColor(leg)}}>{leg.chamber}</td>
      </tr>);

      var table = null;
      var map = null;
      var error = null;

      if (this.state.legislators.length) {
        // have to wrap this in a div or the grid sizing will explode the table
        table = (<div><table id="results">
              <thead>
                <tr>
                  <th></th>
                  <th>Name</th>
                  <th>Party</th>
                  <th>District</th>
                  <th>Chamber</th>
                </tr>
              </thead>
              <tbody>
                  {rows}
              </tbody>
          </table></div>)
      }

      if (this.state.showMap) {
          map = (<Map
            zoom={11}
            lat={this.state.lat}
            lon={this.state.lon}
            legislators={this.state.legislators}
            containerElement={<div style={{ height: `400px` }} />}
            mapElement={<div style={{ height: `100%` }} />}
        />)
      }

      if (this.state.error) {
          error = (<div class="fyl-error">{this.state.error}</div>);
      }

        return (
          <div className="find-your-legislator">
          <div className="input-group">
            <label htmlFor="fyl-address" id="fyl-address-label">Enter Your Address:</label>
            <input className="input-group-field" id="fyl-address" name="address" value={this.state.address} onChange={this.handleAddressChange} />
            <div className="input-group-button">
              <button id="address-lookup" className="button button--primary" onClick={this.geocode}>Search by Address</button>
            </div>
          </div>


          <div className="fyl-locate">
            <button id="locate" className="button button--primary" onClick={this.geolocate}>Use Current Location</button>
          </div>

          {error}
          {table}
          {map}

        </div>
        );
    }

}

// exported from https://mapstyle.withgoogle.com/
const GOOGLE_MAP_STYLES = [
  {
    "elementType": "geometry",
    "stylers": [
      {
        "color": "#f5f5f5"
      }
    ]
  },
  {
    "elementType": "labels.icon",
    "stylers": [
      {
        "visibility": "off"
      }
    ]
  },
  {
    "elementType": "labels.text.fill",
    "stylers": [
      {
        "color": "#616161"
      }
    ]
  },
  {
    "elementType": "labels.text.stroke",
    "stylers": [
      {
        "color": "#f5f5f5"
      }
    ]
  },
  {
    "featureType": "administrative.land_parcel",
    "stylers": [
      {
        "visibility": "off"
      }
    ]
  },
  {
    "featureType": "administrative.land_parcel",
    "elementType": "labels.text.fill",
    "stylers": [
      {
        "color": "#bdbdbd"
      }
    ]
  },
  {
    "featureType": "administrative.neighborhood",
    "stylers": [
      {
        "visibility": "off"
      }
    ]
  },
  {
    "featureType": "poi",
    "elementType": "geometry",
    "stylers": [
      {
        "color": "#eeeeee"
      }
    ]
  },
  {
    "featureType": "poi",
    "elementType": "labels.text",
    "stylers": [
      {
        "visibility": "off"
      }
    ]
  },
  {
    "featureType": "poi",
    "elementType": "labels.text.fill",
    "stylers": [
      {
        "color": "#757575"
      }
    ]
  },
  {
    "featureType": "poi.business",
    "stylers": [
      {
        "visibility": "off"
      }
    ]
  },
  {
    "featureType": "poi.park",
    "elementType": "geometry",
    "stylers": [
      {
        "color": "#e5e5e5"
      }
    ]
  },
  {
    "featureType": "poi.park",
    "elementType": "labels.text.fill",
    "stylers": [
      {
        "color": "#9e9e9e"
      }
    ]
  },
  {
    "featureType": "road",
    "elementType": "geometry",
    "stylers": [
      {
        "color": "#ffffff"
      }
    ]
  },
  {
    "featureType": "road",
    "elementType": "labels",
    "stylers": [
      {
        "visibility": "off"
      }
    ]
  },
  {
    "featureType": "road",
    "elementType": "labels.icon",
    "stylers": [
      {
        "visibility": "off"
      }
    ]
  },
  {
    "featureType": "road.arterial",
    "elementType": "labels.text.fill",
    "stylers": [
      {
        "color": "#757575"
      }
    ]
  },
  {
    "featureType": "road.highway",
    "elementType": "geometry",
    "stylers": [
      {
        "color": "#dadada"
      }
    ]
  },
  {
    "featureType": "road.highway",
    "elementType": "labels.text.fill",
    "stylers": [
      {
        "color": "#616161"
      }
    ]
  },
  {
    "featureType": "road.local",
    "elementType": "labels.text.fill",
    "stylers": [
      {
        "color": "#9e9e9e"
      }
    ]
  },
  {
    "featureType": "transit",
    "stylers": [
      {
        "visibility": "off"
      }
    ]
  },
  {
    "featureType": "transit.line",
    "elementType": "geometry",
    "stylers": [
      {
        "color": "#e5e5e5"
      }
    ]
  },
  {
    "featureType": "transit.station",
    "elementType": "geometry",
    "stylers": [
      {
        "color": "#eeeeee"
      }
    ]
  },
  {
    "featureType": "water",
    "elementType": "geometry",
    "stylers": [
      {
        "color": "#c9c9c9"
      }
    ]
  },
  {
    "featureType": "water",
    "elementType": "labels.text",
    "stylers": [
      {
        "visibility": "off"
      }
    ]
  },
  {
    "featureType": "water",
    "elementType": "labels.text.fill",
    "stylers": [
      {
        "color": "#9e9e9e"
      }
    ]
  }
]

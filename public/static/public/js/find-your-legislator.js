import React from 'react';
import { withGoogleMap, GoogleMap, Marker, Polygon } from "react-google-maps";


function multipolyToPath(coordinates) {
    return coordinates.map(polygon =>
        polygon[0].map(point =>
            ({lat: point[1], lng: point[0]})
        )
    )
}


const Map = withGoogleMap(function(props) {
    var shapes = [];
    for(var leg of props.legislators) {
        if(leg.shape) {
            shapes.push(<Polygon key={leg.division_id}
                defaultPaths={multipolyToPath(leg.shape.coordinates)} />);
        }
    }

    return <GoogleMap defaultZoom={props.zoom}
        center={{ lat: props.lat, lng: props.lon }}>
        <Marker position={{ lat: props.lat, lng: props.lon }} />
        {shapes}
    </GoogleMap>
});


export default class FindYourLegislator extends React.Component {
    constructor (props) {
        super(props);
        const queryParams = new URLSearchParams(window.location.search)
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
        const body = {
            address: this.state.address,
            region: 'us',
        };
        const component = this;
        var geocoder = new google.maps.Geocoder();
        geocoder.geocode(body, function(results, status) {
            if (status === 'OK') {
                component.setState({
                    lat: results[0].geometry.location.lat(),
                    lon: results[0].geometry.location.lng(),
                });
                component.updateLegislators();
            } else {
                component.setError("Unable to geolocate your address, try adding more information.");
            }
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
            <td>{leg.name}</td>
            <td>{leg.party}</td>
            <td>{leg.district}</td>
            <td>{leg.chamber}</td>
        </tr>);

        var table = null;
        var map = null;
        var error = null;

        if (this.state.legislators.length) {
            table = (<table id="results">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Party</th>
                        <th>District</th>
                        <th>Chamber</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>)
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
        <div>
            <h1>Find Your Legislators</h1>
            <label htmlFor="address">Enter Your Address:</label>
            <input id="address" name="address" value={this.state.address} onChange={this.handleAddressChange} />
            <button id="address-lookup" className="button" onClick={this.geocode}>Search by Address</button>
            <button id="locate" className="button" onClick={this.geolocate}>Use Current Location</button>

            {error}
            {table}
            {map}

        </div>
        );
    }

}

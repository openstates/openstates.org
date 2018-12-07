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
            console.log(multipolyToPath(leg.shape.coordinates));
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
        this.state = {
            address: '',
            lat: 0,
            lon: 0,
            legislators: [],
        };
        this.handleAddressChange = this.handleAddressChange.bind(this);
        this.geocode = this.geocode.bind(this);
        this.geolocate = this.geolocate.bind(this);
    }

    handleAddressChange(event) {
      this.setState({address: event.target.value});
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
            console.warn('could not geolocate');
          });
        } else {
            console.warn('could not geolocate');
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
                // TODO 
                console.warn('could not geocode');
            }
        });
    }

    updateLegislators() {
        if(!this.state.lat || !this.state.lon) {
            this.setState({legislators: []});
        } else { 
            const component = this;
            fetch(`/public/find_your_legislator?lat=${this.state.lat}&lon=${this.state.lon}`)
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
                                component.setState({legislators: component.state.legislators});
                            });
                    }
                });
        }

    }

    render() {
        const legTable = this.state.legislators.map(leg => <tr key={leg.name}>
            <td>{leg.name}</td>
            <td>{leg.party}</td>
            <td>{leg.district}</td>
            <td>{leg.chamber}</td>
        </tr>);

        return (
        <div>
            <h1>Find Your Legislators</h1>
            <label htmlFor="address">Enter Your Address:</label>
            <input id="address" name="address" value={this.state.address} onChange={this.handleAddressChange} />
            <button id="address-lookup" className="button" onClick={this.geocode}>Search by Address</button>
            <button id="locate" className="button" onClick={this.geolocate}>Use Current Location</button>

            <table id="results">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Party</th>
                        <th>District</th>
                        <th>Chamber</th>
                    </tr>
                </thead>
                <tbody>
                    {legTable}
                </tbody>
            </table>

            <Map
              zoom={11}
              lat={this.state.lat}
              lon={this.state.lon}
              legislators={this.state.legislators}
              containerElement={<div style={{ height: `400px` }} />}
              mapElement={<div style={{ height: `100%` }} />}
            />
        </div>
        );
    }

}

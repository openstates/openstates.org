import React from "react";
import ReactDOM from "react-dom";
import ReactMapboxGl, {
  Source,
  GeoJSONLayer,
  Layer,
  Marker,
  Feature,
} from "react-mapbox-gl";
import stateBounds from "./state-bounds";
import LegislatorImage from "./legislator-image";
import config from "./config";

function multipolyToPath(coordinates) {
  return coordinates.map(polygon =>
    polygon[0].map(point => ({ lat: point[1], lng: point[0] }))
  );
}

function chamberColor(leg) {
  return leg.chamber === "lower"
    ? config.LOWER_CHAMBER_COLOR
    : config.UPPER_CHAMBER_COLOR;
}

const Map = ReactMapboxGl({
  accessToken: config.MAPBOX_ACCESS_TOKEN,
});

class ResultMap extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    var shapes = [];
    for (var leg of this.props.legislators) {
      if (leg.shape) {
        const color = chamberColor(leg);
        shapes.push(
          <GeoJSONLayer
            key={leg.division_id}
            data={leg.shape}
            linePaint={config.MAP_DISTRICTS_STROKE.paint}
            fillPaint={{ "fill-color": color, "fill-opacity": 0.2 }}
          />
        );
      }
    }
    return (
      <div id="fyl-map-container">
        <Map
          style={config.MAP_BASE_STYLE}
          minZoom={2}
          maxZoom={13}
          interactive={true}
          attributionControl={true}
          center={[this.props.lon, this.props.lat]}
        >
          <Source
            id="sld"
            tileJsonSource={{ type: "vector", url: config.MAP_SLD_SOURCE }}
          />
          {shapes}
          <Layer
            type="symbol"
            id="marker"
            layout={{
              "icon-image": "marker-15",
              "icon-anchor": "bottom",
              "icon-size": 2,
            }}
          >
            <Feature
              coordinates={[this.props.lon, this.props.lat]}
              draggable={true}
              onDragEnd={this.props.handleDrag}
            />
          </Layer>
        </Map>
      </div>
    );
  }
}

export default class FindYourLegislator extends React.Component {
  constructor(props) {
    super(props);
    const queryParams = new URLSearchParams(window.location.search);
    this.state = {
      address: queryParams.get("address") || "",
      lat: queryParams.get("lat") || 0,
      lon: queryParams.get("lon") || 0,
      stateAbbr: queryParams.get("state") || "",
      legislators: [],
      error: "",
    };
    this.handleAddressChange = this.handleAddressChange.bind(this);
    this.handleDrag = this.handleDrag.bind(this);
    this.geocode = this.geocode.bind(this);
    this.geolocate = this.geolocate.bind(this);

    if (this.state.lat && this.state.lon) {
      this.updateLegislators();
    } else if (this.state.address) {
      // if we just got an address, geocode
      this.geocode();
    }
  }

  handleAddressChange(event) {
    this.setState({ address: event.target.value });
  }

  handleDrag(event) {
    this.setState({
      lat: event.lngLat.lat,
      lon: event.lngLat.lng,
    });
    this.updateLegislators();
  }

  setError(message) {
    this.setState({
      error: message,
      legislators: [],
      showMap: false,
    });
  }

  geolocate() {
    const component = this;
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        function(position) {
          component.setState({
            lat: position.coords.latitude,
            lon: position.coords.longitude,
          });
          component.updateLegislators();
        },
        function() {
          component.setError(
            "Geolocation was not available, try entering your address."
          );
        }
      );
    } else {
      component.setError(
        "Geolocation was not available, try entering your address."
      );
    }
  }

  geocode() {
    const component = this;
    // if a state was passed in, limit geocoding to bounding box
    const bb = this.state.stateAbbr ? stateBounds[this.state.stateAbbr] : null;
    const bbStr = this.state.stateAbbr ? `&bbox=${bb[0][0]},${bb[0][1]},${bb[1][0]},${bb[1][1]}` : "";
    const url = `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURI(
      this.state.address
    )}.json?country=US&limit=1${bbStr}&access_token=${config.MAPBOX_ACCESS_TOKEN}`;

    fetch(url)
      .then(response => response.json())
      .then(function(json) {
        component.setState({
          lat: json.features[0].center[1],
          lon: json.features[0].center[0],
        });
        component.updateLegislators();
      })
      .catch(function(error) {
        console.error(error);
        component.setError(
          "Unable to geolocate your address, try adding more information."
        );
      });
  }

  updateLegislators() {
    if (!this.state.lat || !this.state.lon) {
      this.setState({ legislators: [], showMap: false });
    } else {
      const component = this;
      const llUrl = `/find_your_legislator/?lat=${this.state.lat}&lon=${this.state.lon}&address=${this.state.address}&state=${this.state.stateAbbr}`;
      history.pushState(llUrl, "", llUrl);
      fetch(llUrl + "&json=json")
        .then(response => response.json())
        .then(function(json) {
          component.setState({ legislators: json.legislators });

          for (var leg of json.legislators) {
            fetch(
              `https://data.openstates.org/boundaries/2018/${leg.division_id}.json`
            )
              .then(response => response.json())
              .then(function(json) {
                for (var stleg of component.state.legislators) {
                  if (stleg.division_id === json.division_id) {
                    stleg.shape = json.shape;
                  }
                }
                component.setState({
                  legislators: component.state.legislators,
                  showMap: true,
                  error: null,
                });
              });
          }
        });
    }
  }

  render() {
    const rows = this.state.legislators.map(leg => (
      <tr key={leg.name}>
        <td>
          <LegislatorImage id={leg.id} image={leg.image} />
        </td>
        <td>
          <a href={leg.pretty_url}>{leg.name}</a>
        </td>
        <td>{leg.party}</td>
        <td>{leg.district}</td>
        <td style={{ backgroundColor: chamberColor(leg) }}>{leg.chamber}</td>
      </tr>
    ));

    var table = null;
    var map = null;
    var error = null;

    if (this.state.legislators.length) {
      // have to wrap this in a div or the grid sizing will explode the table
      table = (
        <div>
          <table id="results">
            <thead>
              <tr>
                <th></th>
                <th>Name</th>
                <th>Party</th>
                <th>District</th>
                <th>Chamber</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
      );
    }

    if (this.state.showMap) {
      map = (
        <ResultMap
          zoom={11}
          lat={this.state.lat}
          lon={this.state.lon}
          legislators={this.state.legislators}
          handleDrag={this.handleDrag}
        />
      );
    }

    if (this.state.error) {
      error = <div class="fyl-error">{this.state.error}</div>;
    }

    return (
      <div className="find-your-legislator">
        <div className="input-group">
          <label htmlFor="fyl-address" id="fyl-address-label">
            Enter Your Address:
          </label>
          <input
            className="input-group-field"
            id="fyl-address"
            name="address"
            value={this.state.address}
            onChange={this.handleAddressChange}
          />
          <div className="input-group-button">
            <button
              id="address-lookup"
              className="button button--primary"
              onClick={this.geocode}
            >
              Search by Address
            </button>
          </div>
        </div>

        <div className="fyl-locate">
          <button
            id="locate"
            className="button button--primary"
            onClick={this.geolocate}
          >
            Use Current Location
          </button>
        </div>

        {error}
        {table}
        {map}
      </div>
    );
  }
}

window.addEventListener("load", () => {
  const fyl = document.querySelector('[data-hook="find-your-legislator"]');
  ReactDOM.render(React.createElement(FindYourLegislator, {}), fyl);
});

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
      legislators: [
        {
          'name': 'Thom Tillis',
          'id': 'ocd-person/3ad2df38-e817-50b9-924d-9dbd4bba94a8',
          'image': 'https://theunitedstates.io/images/congress/450x550/T000476.jpg',
          'pretty_url': '/person/thom-tillis-1mzvGmdQ5umYtpGF6z1cka/',
          'party': 'Republican',
          'chamber': 'upper',
          'district': 'North Carolina',
          'division_id': 'ocd-division/country:us/state:nc',
          'jurisdiction_id': 'ocd-jurisdiction/country:us/government',
          'level': 'federal'
        },
        {
          'name': 'Richard Burr',
          'id': 'ocd-person/39df75fd-67d3-5a8f-b00b-64bd3a4124f2',
          'image': 'https://theunitedstates.io/images/congress/450x550/B001135.jpg',
          'pretty_url': '/person/richard-burr-1lCgRQO4YvR7zJ80ci3Tda/',
          'party': 'Republican',
          'chamber': 'upper',
          'district': 'North Carolina',
          'division_id': 'ocd-division/country:us/state:nc',
          'jurisdiction_id': 'ocd-jurisdiction/country:us/government',
          'level': 'federal'
        },
        {
          'name': 'David E. Price',
          'id': 'ocd-person/3da2a16b-4772-5dc1-837a-87f7b3894dec',
          'image': 'https://theunitedstates.io/images/congress/450x550/P000523.jpg',
          'pretty_url': '/person/david-e-price-1sIqxyVSOfBtfQDG3CJqBg/',
          'party': 'Democratic',
          'chamber': 'lower',
          'district': 'NC-4',
          'division_id': 'ocd-division/country:us/state:nc/cd:4',
          'jurisdiction_id': 'ocd-jurisdiction/country:us/government',
          'level': 'federal'
        },
        {
          'name': 'Allison A. Dahle',
          'id': 'ocd-person/785927b3-34ca-4a2d-bc1c-df4cc8e16c47',
          'image': 'https://www.ncleg.gov/Members/MemberImage/H/740/High',
          'pretty_url': '/person/allison-a-dahle-3f5p2T60GXSTUrr6UwHGuV/',
          'party': 'Democratic',
          'chamber': 'lower',
          'district': '11',
          'division_id': 'ocd-division/country:us/state:nc/sldl:11',
          'jurisdiction_id': 'ocd-jurisdiction/country:us/state:nc/government',
          'level': 'state'
        },
        {
          'name': 'Wiley Nickel',
          'id': 'ocd-person/62cd36df-969c-4a51-b548-11740357ee79',
          'image': 'https://www.ncleg.gov/Members/MemberImage/S/409/High',
          'pretty_url': '/person/wiley-nickel-30R1wBB8pxXn6wfCNTG8l7/',
          'party':' Democratic',
          'chamber': 'upper',
          'district': '16',
          'division_id': 'ocd-division/country:us/state:nc/sldu:16',
          'jurisdiction_id': 'ocd-jurisdiction/country:us/state:nc/government',
          'level': 'state',
        }
      ],
      stateLegislators:[],
      federalLegislators:[],
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
    } else if (queryParams.get("geolocate")) {
      this.geolocate();
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
    const bbStr = this.state.stateAbbr
      ? `&bbox=${bb[0][0]},${bb[0][1]},${bb[1][0]},${bb[1][1]}`
      : "";
    const url = `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURI(
      this.state.address
    )}.json?country=US&limit=1${bbStr}&access_token=${
      config.MAPBOX_ACCESS_TOKEN
    }`;

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

  splitLegislators() {
    this.state.legislators.map(leg => {
      const level = leg.level;
      if (level === 'state')
        return this.state.stateLegislators.push(leg);
      this.state.federalLegislators.push(leg);
    });
  }

  render() {
    this.splitLegislators();
    const rows = this.state.legislators.map(leg => (
      <tr key={leg.name}>
        <td>
          <LegislatorImage id={leg.id} image={leg.image} party={leg.party} />
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
      error = <div className="fyl-error">{this.state.error}</div>;
    }

    return (
      <div className="find-your-legislator">
        <div className="input-group">
          <label htmlFor="fyl-address" id="fyl-address-label">
            Enter Your Address:
          </label>
          <input
            className="input-group-field"
            type="search"
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

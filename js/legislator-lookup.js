import React, { useState } from "react";
import ReactDOM from "react-dom";
import config from "./config";

function chamberColor() {
  return "blue";
}

function LegislatorRow(props) {
  return (
    <tr key={props.leg.name}>
      <td>
        <a href={props.leg.url}>{props.leg.name}</a>
      </td>
      <td>{props.leg.party}</td>
      <td>{props.leg.district}</td>
      <td>{props.leg.chamber}</td>
    </tr>
  );
}

function LegislatorLookup() {
  const [address, setAddress] = useState("");
  const [location, setLocation] = useState({ lat: 0, lng: 0 });
  const [legislators, setLegislators] = useState([]);
  const [error, setError] = useState("");

  function updateLegislators(loc) {
    if (!loc.lat || !loc.lng) {
      setLegislators([]);
    } else {
      const url = `https://v3.openstates.org/people.geo?lat=${loc.lat}&lng=${loc.lng}&apikey=${config.OPENSTATES_API_KEY}`;
      fetch(url)
        .then((response) => response.json())
        .then(function (json) {
          setLegislators(json.results);
        });
    }
  }

  function geocode() {
    const url = `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURI(
      address
    )}.json?country=US&limit=1&access_token=${config.MAPBOX_ACCESS_TOKEN}`;

    fetch(url)
      .then((response) => response.json())
      .then(function (json) {
        const newLocation = {
          lat: json.features[0].center[1],
          lng: json.features[0].center[0],
        };
        setLocation(newLocation);
        updateLegislators(newLocation);
      })
      .catch(function (error) {
        console.error(error);
        component.setError(
          "Unable to geolocate your address, try adding more information."
        );
      });
  }

  return (
    <div className="osw-legislator-lookup">
      <div>
        <label htmlFor="osw-address" id="osw-address-label">
          Enter Your Address:
        </label>
        <input
          type="search"
          id="osw-address"
          name="address"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
        />
        <input type="submit" id="osw-submit" value="Search" onClick={geocode} />
      </div>

      <div>
        <table>{legislators.map((leg) => <LegislatorRow leg={leg} />)}</table>
      </div>
    </div>
  );
}

ReactDOM.render(
  React.createElement(LegislatorLookup),
  document.getElementById("osw-c")
);

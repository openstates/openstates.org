import React, { useState } from "react";
import ReactDOM from "react-dom";
import config from "./config";

function chamberColor() {
  return "blue";
}

function chamberDisplay(leg) {
  const abbr = leg.jurisdiction.id.split("/")[2].split(":")[1].toUpperCase();
  const classification = leg.current_role.org_classification;
  let chamber = "";
  if (classification === "upper") {
    chamber = "Senate";
  } else if (classification === "lower") {
    chamber = "House";
    // TODO: assembly
  }
  return abbr + " " + chamber;
}

function LegislatorRow(props) {
  return (
    <tr key={props.leg.name}>
      <td>
        <a href={props.leg.openstates_url}>{props.leg.name}</a>
      </td>
      <td>{props.leg.party}</td>
      <td>{props.leg.current_role.district}</td>
      <td>{chamberDisplay(props.leg)}</td>
    </tr>
  );
}

export default function LegislatorLookup(props) {
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

  if (legislators.length === 0) {
    return (
      <div
        className="osw-legislator-lookup"
        style={{ backgroundColor: props.bgColor, color: props.fgColor }}
      >
        <h2>Find Your State Representatives</h2>
        <div>
          <label htmlFor="osw-address" id="osw-address-label">
            Enter Your Address (
            <abbr title="Zip code alone isn't enough to uniquely identify legislative districts.">
              ?
            </abbr>
            )
          </label>
          <input
            type="search"
            id="osw-address"
            name="address"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
          />
          <input
            type="submit"
            className="button"
            style={{
              color: props.buttonTextColor,
              backgroundColor: props.buttonColor,
            }}
            value="Search"
            onClick={geocode}
          />
        </div>
      </div>
    );
  } else {
    return (
      <div
        className="osw-legislator-lookup"
        style={{ backgroundColor: props.bgColor, color: props.fgColor }}
      >
        <h2>Your State Representatives</h2>
        <div className="osw-results">
          <table className="osw-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Party</th>
                <th>District</th>
                <th>Chamber</th>
              </tr>
            </thead>
            <tbody>
              {legislators.map((leg) => (
                <LegislatorRow leg={leg} key={leg.id} />
              ))}
            </tbody>
          </table>
        </div>
        <input
          type="submit"
          className="button"
          style={{
            color: props.buttonTextColor,
            backgroundColor: props.buttonColor,
          }}
          value="Back"
          onClick={() => setLegislators([])}
        />
      </div>
    );
  }
}

LegislatorLookup.defaultProps = {
  bgColor: "#ffffff",
  fgColor: "#222222",
  buttonColor: "#002f5a",
  buttonTextColor: "#ffffff",
};

const create_widget = () => {
  const elem = document.getElementById("osw-c");
  if (elem) {
    const widgetConfig = JSON.parse(
      document.getElementById("config").textContent
    );
    ReactDOM.render(React.createElement(LegislatorLookup, widgetConfig), elem);
  }
};
create_widget();

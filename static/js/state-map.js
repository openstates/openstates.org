import React from "react";
import ReactDOM from "react-dom";
import ReactMapboxGl, { Source, Layer } from "react-mapbox-gl";
import stateBounds from "./state-bounds";
import config from "./config";

const Map = ReactMapboxGl({
  accessToken: config.MAPBOX_ACCESS_TOKEN,
});

export default class StateMap extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      chamberType: ["dc", "ne"].includes(props.state) ? "sldu" : "sldl",
    };
  }

  buttonGroup() {
    if (this.props.chambers.lower) {
      return (
        <div className="button-group">
          <button
            className={
              this.state.chamberType === "sldl"
                ? "button button--active"
                : "button"
            }
            onClick={() => this.setState({ chamberType: "sldl" })}
          >
            {this.props.chambers.lower}
          </button>
          <button
            className={
              this.state.chamberType === "sldu"
                ? "button button--active"
                : "button"
            }
            onClick={() => this.setState({ chamberType: "sldu" })}
          >
            {this.props.chambers.upper}
          </button>
        </div>
      );
    }
  }

  render() {
    const filter = [
      "all",
      ["==", "state", this.props.state],
      ["==", "type", this.state.chamberType],
    ];
    return (
      <div id="state-map-container">
        <Map
          style={config.MAP_BASE_STYLE}
          minZoom={2}
          maxZoom={13}
          interactive={true}
          fitBounds={stateBounds[this.props.state]}
          fitBoundsOptions={{ padding: 25, animate: false }}
        >
          <Source
            id="sld"
            tileJsonSource={{ type: "vector", url: config.MAP_SLD_SOURCE }}
          />
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
        {this.buttonGroup()}
      </div>
    );
  }
}

window.addEventListener("load", () => {
  const sm = document.querySelector('[data-hook="state-map"]');
  if (sm) {
    ReactDOM.render(
      React.createElement(StateMap, {
        state: sm.getAttribute("data-state"),
        chambers: window.chambers,
      }),
      sm
    );
  }
});

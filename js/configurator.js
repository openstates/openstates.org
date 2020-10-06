import React, { useState } from "react";
import ReactDOM from "react-dom";
import LegislatorLookup from "./legislator-lookup";

function OptionInput(props) {
  // props.name, props.value, props.setConfigValue

  return (
    <div>
      <label htmlFor={props.name}>{props.name}</label>
      <input
        id={props.name}
        name={props.name}
        value={props.value}
        onChange={(e) => props.setConfigValue(props.name, e.target.value)}
      />
    </div>
  );
}

function getInitialState(options) {
  let state = {
    "name": "My Widget",
  };

  for(let opt of options) {
    state[opt.name] = opt.default;
  }
  return state;
}


function Configurator(props) {
  // TODO: get this from props widget type
  const options = [
    { name: "bgColor", type: "color", default: "000000" },
    { name: "fgColor", type: "color", default: "ffffff" },
  ];

  const [config, setConfig] = useState(getInitialState(options));
  const PreviewElement = LegislatorLookup;

  function setConfigValue(name, value) {
    let newConfig = Object.assign({}, config);
    newConfig[name] = value;
    setConfig(newConfig);
  }

  return (
    <div class="config-grid">
      <div>
        <h2>Configuration</h2>

        <OptionInput
          name="name"
          value={config.name}
          setConfigValue={setConfigValue}
        />
        {options.map((o) => (
          <OptionInput
            key={o.name}
            name={o.name}
            type={o.type}
            value={config[o.name]}
            setConfigValue={setConfigValue}
          />
        ))}
      </div>
      <div>
        <PreviewElement />
      </div>
    </div>
  );
}

ReactDOM.render(
  React.createElement(Configurator),
  document.getElementById("configurator")
);

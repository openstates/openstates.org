import React from "react";
import ReactDOM from "react-dom";

export function addDataHookListener(dataHookName, contextId, reactComponent) {
  window.addEventListener("load", () => {
    const div = document.querySelector(`[data-hook="${dataHookName}"]`);
    if (div) {
      var context = JSON.parse(document.getElementById(contextId).textContent);
      ReactDOM.render(React.createElement(reactComponent, context), div);
    }
  });
}


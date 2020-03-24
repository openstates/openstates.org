import React from "react";
import ReactDOM from "react-dom";
import AccountsOverview from "./account-overview";
import APIDashboard from "./api-dashboard";

window.addEventListener("load", () => {
  const div = document.querySelector('[data-hook="account-overview"]');
  if (div) {
    var context = JSON.parse(document.getElementById("context").textContent);
    ReactDOM.render(React.createElement(AccountsOverview, context), div);
  }
});

window.addEventListener("load", () => {
  const div = document.querySelector('[data-hook="api-dashboard"]');
  if (div) {
    var context = JSON.parse(document.getElementById("context").textContent);
    ReactDOM.render(React.createElement(APIDashboard, context), div);
  }
});

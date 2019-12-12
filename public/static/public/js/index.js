import "../styles/app.scss";

// polyfills (IE 11)
import "url-search-params-polyfill";
import "promise-polyfill/src/polyfill";
import "whatwg-fetch";

import React from "react";
import ReactDOM from "react-dom";

import LegislatorList from "./legislator-list";
import CommitteeList from "./committee-list";
import LegislatorImage from "./legislator-image";

function addBanner(content) {
  var div = document.createElement("div");
  div.className = "notification-banner";
  div.appendChild(document.createTextNode(content));
  document.querySelector("body header").appendChild(div);
}

function checkIE() {
  var ua = window.navigator.userAgent;
  if (ua.indexOf("MSIE") > 0 || ua.indexOf("Trident/") > 0) {
    document.querySelector(".header__logo").src =
      "/static/public/images/openstates_logo.png";
    addBanner(
      "You are viewing this site in an outdated browser, some features may not work."
    );
  }
}

window.addEventListener("load", () => {
  const ll = document.querySelector('[data-hook="legislator-list"]');
  if (ll) {
    ReactDOM.render(
      React.createElement(LegislatorList, {
        legislators: window.legislators,
        chambers: window.chambers,
      }),
      ll
    );
  }

  const cl = document.querySelector('[data-hook="committee-list"]');
  if (cl) {
    ReactDOM.render(
      React.createElement(CommitteeList, {
        committees: window.committees,
        chambers: window.chambers,
      }),
      cl
    );
  }

  const images = document.querySelectorAll('[data-hook="legislator-image"]');
  for (var img of images) {
    ReactDOM.render(
      React.createElement(LegislatorImage, {
        image: img.getAttribute("data-image"),
        id: img.getAttribute("data-person-id"),
        size: img.getAttribute("data-size"),
      }),
      img
    );
  }

  checkIE();
});

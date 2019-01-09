import '../styles/app.scss'

import 'url-search-params-polyfill';

import React from 'react'
import ReactDOM from 'react-dom'

import DistrictMap from './legislator-map'
import StateMap from './state-map'
import LegislatorList from './legislator-list'
import FindYourLegislator from './find-your-legislator'
import CommitteeList from './committee-list'
import LegislatorImage from './legislator-image'


window.addEventListener('load', () => {
    const dm = document.querySelector('[data-hook="legislator-map"]');
    if (dm) {
        ReactDOM.render(React.createElement(
            DistrictMap,
            {
                districtId: dm.getAttribute('data-division-id'),
                state: dm.getAttribute('data-state')
            }),
            dm
        );
    }

    const sm = document.querySelector('[data-hook="state-map"]');
    if (sm) {
        ReactDOM.render(React.createElement(
            StateMap,
            {
                state: sm.getAttribute('data-state'),
                chambers: window.chambers
            }),
            sm
        );
    }

    const ll = document.querySelector('[data-hook="legislator-list"]');
    if(ll) {
        ReactDOM.render(React.createElement(
            LegislatorList,
            {legislators: window.legislators, chambers: window.chambers}),
            ll
        );
    }

    const cl = document.querySelector('[data-hook="committee-list"]');
    if(cl) {
        ReactDOM.render(React.createElement(
            CommitteeList,
            {committees: window.committees, chambers: window.chambers}),
            cl
        );
    }

    const fyl = document.querySelector('[data-hook="find-your-legislator"]');
    if (fyl) {
        ReactDOM.render(React.createElement(FindYourLegislator, {}), fyl);
    }

  const images = document.querySelectorAll('[data-hook="legislator-image"]');
  for (var img of images) {
    ReactDOM.render(React.createElement(
      LegislatorImage,
      {
        image: img.getAttribute("data-image"),
        id: img.getAttribute("data-person-id"),
        size: img.getAttribute("data-size"),
      }),
      img
    );
  }

})

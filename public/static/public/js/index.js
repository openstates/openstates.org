import '../styles/app.scss'

import React from 'react'
import ReactDOM from 'react-dom'

import DistrictMap from './legislator-map'
import StateMap from './state-map'
import LegislatorList from './legislator-list'
import FindYourLegislator from './find-your-legislator'
import CommitteeList from './committee-list'


window.imgError = function(t) {
    // handle Event or Element
    if(t.target) {
        t = t.target;
    }
    var placeholder = document.createElement('div');
    placeholder.classList.add("thumbnail", "thumbnail--placeholder");
    t.parentNode.replaceChild(placeholder, t);
}


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
})

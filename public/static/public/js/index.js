import '../styles/app.scss'

import React from 'react'
import ReactDOM from 'react-dom'

import legislatorMap from './legislator-map'
import LegislatorList from './legislator-list'
import FindYourLegislator from './find-your-legislator'


window.addEventListener('load', () => {
  if (document.querySelector('[data-hook="legislator-map"]')) {
    legislatorMap()
  }

  if (document.querySelector('[data-hook="legislator-list"]')) {
    ReactDOM.render(
      React.createElement(LegislatorList, {legislators: window.props}),
      window.reactMount
    )
  }

    const fyl = document.querySelector('[data-hook="find-your-legislator"]');
    if (fyl) {
        ReactDOM.render(React.createElement(FindYourLegislator, {}), fyl);
    }
})

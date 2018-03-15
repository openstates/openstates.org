import '../styles/app.scss'

import React from 'react'
import ReactDOM from 'react-dom'

import legislatorMap from './legislator-map'
import LegislatorList from './legislator-list'

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
})

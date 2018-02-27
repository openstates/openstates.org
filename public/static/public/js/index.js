import '../styles/app.scss'

import React from 'react'
import ReactDOM from 'react-dom'

import legislatorMap from './legislator-map'


ReactDOM.render(
  <p>Open States + React!</p>,
  document.querySelector('[data-hook="react-mount"]')
);


console.log('Hello, Open States!')

if (document.querySelector('[data-hook="legislator-map"]')) {
  legislatorMap()
}

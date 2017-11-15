import React from 'react';
import ReactDOM from 'react-dom';
import { HashRouter, Route, Switch } from 'react-router-dom';
import './styles/main.css';
import registerServiceWorker from './registerServiceWorker';

import App from './views/app';
import Home from './views/home';
import Bill from './views/bill';
import Legislator from './views/legislator';

ReactDOM.render((
  <HashRouter>
    <Route path='/' component={App}>
      <Switch>
        <Route path='/' component={Home} />
        <Route path='/legislators/:legislatorID' component={Legislator} />
        <Route path='/bills/:billID' component={Bill} />
      </Switch>
    </Route>
  </HashRouter>
), document.getElementById('root'));

registerServiceWorker();

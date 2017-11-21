import React from 'react';
import ReactDOM from 'react-dom';
import { HashRouter, Route, Switch } from 'react-router-dom';
import './styles/main.css';
import registerServiceWorker from './registerServiceWorker';

import Home from './views/home';
import State from './views/state';
import Bill from './views/bill';
import Legislators from './views/legislators';
import Legislator from './views/legislator';

import Header from './components/header';
import Footer from './components/footer';

ReactDOM.render((
  <HashRouter>
    <div className="App">
      <Route path='/' exact component={Home} />
      <Route path='/:state' component={Header} />
      <main>
        <Switch>
          <Route path='/:state' exact component={State} />
          <Route path='/:state/legislators' exact component={Legislators} />
          <Route path='/:state/legislators/:legislatorID*' component={Legislator} />
          <Route path='/:state/bills/:billID' component={Bill} />
        </Switch>
      </main>
      <Footer />
    </div>
  </HashRouter>
), document.getElementById('root'));

registerServiceWorker();

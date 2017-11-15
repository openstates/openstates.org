import React, { Component } from 'react';

export default class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <h1 className="App-title">Welcome to React</h1>
        </header>
        <body>
          {JSON.stringify(this.props)}
        </body>
        <footer>
        </footer>
      </div>
    );
  }
}

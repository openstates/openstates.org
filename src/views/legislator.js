import React, { Component } from 'react';

export default class Legislator extends Component {
  render() {
    return (
      <div className="Legislator">
        <p>Legislator ID: {this.props.match.params.legislatorID}</p>
      </div>
    );
  }
}

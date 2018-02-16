import React, { Component } from 'react';

export default class State extends Component {
  render() {
    return (
      <div>
        State homepage for {this.props.match.params.state}
      </div>
    );
  }
}

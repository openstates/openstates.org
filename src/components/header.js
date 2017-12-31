import React, { Component } from 'react';
import { Link } from 'react-router-dom';

const MOCK_DATA = [
  {
    abbr: 'ak',
    name: 'Alaska'
  },
  {
    abbr: 'al',
    name: 'Alabama'
  },
  {
    abbr: 'az',
    name: 'Arizona'
  }
];

export default class Header extends Component {
  constructor (props) {
    super(props);
    this.state = {
      state: this.props.match.params.state
    };
    this.handleStateSelect = this.handleStateSelect.bind(this);
  }

  handleStateSelect (e) {
    const state = e.target.value;
    const path = `/${state}`;
    this.setState({state: state});
    this.props.history.push(path);
  }

  render () {
    return (
      <div>
        <select
          value={this.state.state}
          onChange={this.handleStateSelect}
        >
          {
            MOCK_DATA.map(st =>
              <option key={st.abbr} value={st.abbr}>{st.name}</option>
            )
          }
        </select>
        <Link to={`/${this.props.match.params.state}`}>Overview</Link>
        <Link to={`/${this.props.match.params.state}/Legislators`}>Legislators</Link>
        <Link to={`/${this.props.match.params.state}/Bills`}>Bills</Link>
      </div>
    );
  }
};

import React, { Component } from 'react';
import { Link } from 'react-router-dom';

const MOCK_DATA = [
  {
    image: '/abrams.jpg',
    name: 'Abby Abrams',
    party: 'Democrat',
    district: '1',
    chamber: 'lower',
    id: 'ocd-person/c657b0d6-6962-4770-892e-45278d65ed43'
  },
  {
    image: '/bonds.jpg',
    name: 'Barry Bonds',
    party: 'Democrat',
    district: '2',
    chamber: 'lower',
    id: 'ocd-person/a7f548ae-1ddc-416c-aca0-622581e18577'
  },
  {
    image: '/chaplin.jpg',
    name: 'Charlie Chaplin',
    party: 'Republican',
    district: '1',
    chamber: 'upper',
    id: 'ocd-person/86a9bb56-f0d9-4fb9-b906-41a2ac864f90'
  }
];

export default class Legislators extends Component {
  render() {
    return (
      <div className="Legislators">
        <table>
          <thead>
            <tr>
              <th></th>
              <th>Name</th>
              <th>Party</th>
              <th>District</th>
              <th>Chamber</th>
            </tr>
          </thead>
          <tbody>
            {
              MOCK_DATA.map(leg =>
                <tr key={`${leg.chamber}-${leg.district}-${leg.name}`}>
                  <td>
                    <img href={leg.image} alt={`${leg.name} headshot`} />
                  </td>
                  <td>
                    <Link to={`/${this.props.match.params.state}/legislators/${leg.id}`}>
                      {leg.name}
                    </Link>
                  </td>
                  <td>{leg.party}</td>
                  <td>{leg.district}</td>
                  <td>{leg.chamber}</td>
                </tr>
              )
            }
          </tbody>
        </table>
      </div>
    );
  }
}

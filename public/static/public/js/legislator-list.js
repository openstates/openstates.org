import _ from 'lodash'
import React from 'react'

export default class LegislatorList extends React.Component {
  constructor (props) {
    super(props)
    const queryParams = new URLSearchParams(window.location.search)
    this.state = {
      order: 'asc',
      orderBy: 'name',
      chamber: queryParams.get('chamber') || null
    }
  }

  setSortOrder (field) {
    this.setState({
      order: (
        this.state.orderBy !== field
          ? 'asc'
          : this.state.order === 'asc' ? 'desc' : 'asc'
      ),
      orderBy: field
    })
  }

  setChamber (chamber) {
    this.setState({chamber})

    const queryParams = new URLSearchParams(window.location.search)
    if (chamber) {
      queryParams.set('chamber', chamber)
    } else {
      queryParams.delete('chamber')
    }
    const relativePath = queryParams.toString()
      ? `${window.location.pathname}?${queryParams.toString()}`
      : window.location.pathname
    history.pushState(null, '', relativePath)
  }

  render () {
    return (
      <div>
        <div className="button-group">
          <button type="button" onClick={() => this.setChamber('upper')} className={`button ${this.state.chamber === 'upper' ? 'button--active' : ''}`}>Upper Chamber</button>
          <button type="button" onClick={() => this.setChamber('lower')} className={`button ${this.state.chamber === 'lower' ? 'button--active' : ''}`}>Lower Chamber</button>
          <button type="button" onClick={() => this.setChamber(null)} className={`button ${this.state.chamber === null ? 'button--active' : ''}`}>Both Chambers</button>
        </div>

        <table>
          <thead>
            <tr>
              <th></th>
              <th onClick={() => this.setSortOrder('name')}>Name</th>
              <th onClick={() => this.setSortOrder('party')}>Party</th>
              <th onClick={() => this.setSortOrder('district')}>District</th>
              <th onClick={() => this.setSortOrder('chamber')}>Chamber</th>
            </tr>
          </thead>
          <tbody>
            {_.orderBy(this.props.legislators, [this.state.orderBy], [this.state.order])
              .filter(legislator => this.state.chamber === null || legislator.chamber === this.state.chamber)
              .map(b =>
                <tr key={b.id}>
                  <td>
                    {b.headshot_url
                      ? <img src={b.headshot_url} alt={`headshot for ${b.name}`} />
                      : <img alt="placeholder headshot" />
                    }
                  </td>
                  <td><a href={`${window.location.href.split('?')[0]}/${b.id}`}>{b.name}</a></td>
                  <td>{b.party}</td>
                  <td>{b.district}</td>
                  <td>{b.chamber}</td>
                </tr>
              )
            }
          </tbody>
        </table>
      </div>
    )
  }
}

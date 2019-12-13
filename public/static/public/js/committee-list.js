import React from "react";
import ReactDOM from "react-dom";
import LegislatorList, { ChamberButtons } from "./legislator-list";

export default class CommitteeList extends LegislatorList {
  render() {
    return (
      <div>
        <ChamberButtons
          chambers={this.props.chambers}
          chamber={this.state.chamber}
          setChamber={this.setChamber}
        />
        <table>
          <thead>
            <tr>
              <th onClick={() => this.setSortOrder("name")}>Name</th>
              <th onClick={() => this.setSortOrder("chamber")}>Chamber</th>
              <th onClick={() => this.setSortOrder("member_count")}>Members</th>
            </tr>
          </thead>
          <tbody>
            {_.orderBy(
              this.props.committees,
              [this.state.orderBy],
              [this.state.order]
            )
              .filter(
                committee =>
                  this.state.chamber === null ||
                  committee.chamber === this.state.chamber
              )
              .map(b => (
                <tr key={b.id}>
                  <td>
                    <a href={b.pretty_url}>{b.name}</a>
                  </td>
                  <td>{this.props.chambers[b.chamber]}</td>
                  <td>{b.member_count}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    );
  }
}


window.addEventListener("load", () => {
  const cl = document.querySelector('[data-hook="committee-list"]');
  if (cl) {
    ReactDOM.render(
      React.createElement(CommitteeList, {
        committees: window.committees,
        chambers: window.chambers,
      }),
      cl
    );
  }
});

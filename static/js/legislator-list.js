import _ from "lodash";
import React from "react";
import ReactDOM from "react-dom";
import LegislatorImage from "./legislator-image";

export function ChamberButtons(props) {
  if (Object.keys(props.chambers).length > 1) {
    return (
      <div className="button-group">
        <button
          type="button"
          onClick={() => props.setChamber("upper")}
          className={`button ${
            props.chamber === "upper" ? "button--active" : ""
          }`}
        >
          {props.chambers.upper}
        </button>
        <button
          type="button"
          onClick={() => props.setChamber("lower")}
          className={`button ${
            props.chamber === "lower" ? "button--active" : ""
          }`}
        >
          {props.chambers.lower}
        </button>
        <button
          type="button"
          onClick={() => props.setChamber(null)}
          className={`button ${props.chamber === null ? "button--active" : ""}`}
        >
          Both Chambers
        </button>
      </div>
    );
  } else {
    return "";
  }
}

export default class LegislatorList extends React.Component {
  constructor(props) {
    super(props);
    const queryParams = new URLSearchParams(window.location.search);
    this.state = {
      order: "asc",
      orderBy: "name",
      chamber: queryParams.get("chamber") || null,
    };

    this.setChamber = this.setChamber.bind(this);
  }

  setSortOrder(field) {
    this.setState({
      order:
        this.state.orderBy !== field
          ? "asc"
          : this.state.order === "asc"
          ? "desc"
          : "asc",
      orderBy: field,
    });
  }

  setChamber(chamber) {
    this.setState({ chamber });

    const queryParams = new URLSearchParams(window.location.search);
    if (chamber) {
      queryParams.set("chamber", chamber);
    } else {
      queryParams.delete("chamber");
    }
    const relativePath = queryParams.toString()
      ? `${window.location.pathname}?${queryParams.toString()}`
      : window.location.pathname;
    history.pushState(null, "", relativePath);
  }

  getSortArrowFor(field) {
    // render an arrow for field if it is currently used to sort
    // otherwise return nothing
    console.log(field, this.state.orderBy, this.state.order);
    if(field === this.state.orderBy) {
      return this.state.order === "asc" ? "↓" : "↑";
    }
    return "";
  }

  render() {
    return (
      <div>
        <ChamberButtons
          chambers={this.props.chambers}
          chamber={this.state.chamber}
          setChamber={this.setChamber}
        />
        <table className="hover">
          <thead>
            <tr>
              <th></th>
              <th onClick={() => this.setSortOrder("name")} className="clickable">
                Name
                  {this.getSortArrowFor("name")}
              </th>
              <th onClick={() => this.setSortOrder("current_role.party")} className="clickable">
                Party
                  {this.getSortArrowFor("current_role.party")}
              </th>
              <th onClick={() => this.setSortOrder("current_role.district")} className="clickable">
                District
                  {this.getSortArrowFor("current_role.district")}
              </th>
              {this.props.chambers.lower && (
                <th onClick={() => this.setSortOrder("current_role.chamber")} className="clickable">
                  Chamber
                  {this.getSortArrowFor("current_role.chamber")}
                </th>
              )}
            </tr>
          </thead>
          <tbody>
            {_.orderBy(
              this.props.legislators,
              [this.state.orderBy],
              [this.state.order]
            )
              .filter(
                legislator =>
                  this.state.chamber === null ||
                  legislator.current_role.chamber === this.state.chamber
              )
              .map(b => (
                <tr key={b.id}>
                  <td>
                    <a href={b.pretty_url}>
                      <LegislatorImage id={b.id} image={b.image} party={b.current_role.party} />
                    </a>
                  </td>
                  <td>
                    <a href={b.pretty_url}>{b.name}</a>
                  </td>
                  <td>{b.current_role.party}</td>
                  <td>{b.current_role.district}</td>
                  {this.props.chambers.lower && (
                    <td>{this.props.chambers[b.current_role.chamber]}</td>
                  )}
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    );
  }
}

import React from "react";

export default class LegislatorImage extends React.Component {
  constructor(props) {
    super(props);

    if (props.id && props.image) {
      this.state = {
        url: "https://data.openstates.org/images/small/" + props.id,
      };
    } else {
      this.state = {
        url: null,
      };
    }
  }

  render() {
    const component = this;
    const modifier = this.props.size === "medium" ? "" : "thumbnail--small";
    const containerModifier =
      this.props.size === "medium" ? "--medium mr1" : "--small";
    let containerColor = "#ffdd03";
    if (this.props.party === "Democratic") {
      containerColor = "#00abff";
    } else if (this.props.party == "Republican") {
      containerColor = "#9e0e44";
    }
    let inner = null;
    if (!this.state.url) {
      inner = (
        <img
          className={"thumbnail " + modifier}
          src="/static/images/person.svg"
        />
      );
    } else {
      inner = (
        <img
          className={"thumbnail " + modifier}
          src={this.state.url}
          alt="headshot for legislator"
          onError={() => component.setState({ url: null })}
        />
      );
    }
    return (
      <div
        className={"thumbnail-container" + containerModifier}
        style={{ backgroundColor: containerColor }}
      >
        {inner}
      </div>
    );
  }
}

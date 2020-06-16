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
    const containerModifier = this.props.size === "medium" ? "--medium mr1" : "--small";
    let containerColor = "#ffdd03f";
    if(this.props.party === "Democratic") {
      containerColor = "#00abff";
    } else if (this.props.party == "Republican") {
      containerColor = "#9e0e44";
    }
    if (!this.state.url) {
      return (
        <div className={"thumbnail-container" + containerModifier } style={{backgroundColor: containerColor}}>
          <div className={"thumbnail thumbnail--placeholder " + modifier}></div>
        </div>
      );
    } else {
      return (
        <div className={"thumbnail-container" + containerModifier } style={{backgroundColor: containerColor}}>
        <img
          className={"thumbnail " + modifier}
          src={this.state.url}
          alt="headshot for legislator"
          onError={() => component.setState({ url: null })}
        />
        </div>
      );
    }
  }
}

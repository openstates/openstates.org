import React from 'react';


export default class LegislatorImage extends React.Component {
  constructor(props) {
    super(props);

    if(props.id && props.image) {
      this.state = {
        url: "https://data.openstates.org/images/small/" + props.id
      }
    } else {
      this.state = {
        url: null
      }
    }
  }

  render() {
    const component = this;
    if(!this.state.url) {
      return <div className="thumbnail thumbnail--placeholder thumbnail--small"></div>;
    } else {
      return (<img className="thumbnail thumbnail--small" src={this.state.url} alt="headshot for legislator" onError={() => component.setState({url: null})} />)
    }
  }
}

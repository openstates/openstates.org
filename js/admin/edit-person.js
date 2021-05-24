import React from 'react';
import Cookies from "js-cookie";

class EditPerson extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      submitSuccess: false,
    }
    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleInputChange(event) {
    const { value, name } = event.target;

    this.setState({
      [name]: value
    });
  }

  handleSubmit(event) {
    const csrftoken = Cookies.get("csrftoken");
    event.preventDefault();
  }

  renderInputs(prop) {
    return <input type="text" name={prop} id={prop} onChange={this.handleInputChange} />
  }

  render() {
    const { submitSuccess } = this.state;
    const inputs = this.props.forEach((prop) => {this.renderInputs(prop)});

    return(
      <div>
      {submitSuccess ? (
        <p>Legislator updated successfully.</p>
        ) : (
        <form onSubmit={this.handleSubmit}>
          {inputs}
          <input type="submit" className="button--primary button" value="Submit" />
        </form>
        )}
      </div>
    )
  }
}

export default EditPerson;

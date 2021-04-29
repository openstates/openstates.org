import React from 'react';
import Cookies from "js-cookie";

class NewPersonForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      submitSuccess: false,
    }
    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleInputChange(event) {
    const target = event.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const name = target.name;

    this.setState({
      [name]: value
    });
  }

  handleSubmit(event) {
    const csrftoken = Cookies.get("csrftoken");
    event.preventDefault();
  }

  render() {
    const { submitSuccess } = this.state;

    return(
      <div>
      {submitSuccess ? (
        <p>New legislator added successfully.</p>
        ) : (
        <form onSubmit={this.handleSubmit}>
          <input type="submit" className="button--primary button" value="Submit" />
        </form>
        )}
      </div>
    )
  }
}

export default NewPersonForm;

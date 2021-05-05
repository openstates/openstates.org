import React from 'react';
import Cookies from "js-cookie";

class NewPersonForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      submitSuccess: false,
      state: this.props.state,
      name: '',
      district: '',
      chamber: 'house',
    }
    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleInputChange(event) {
    const target = event.target;
    const { value, name } = target;

    this.setState({
      [name]: value
    });
  }

  handleSubmit(event) {
    const csrftoken = Cookies.get("csrftoken");
    const url = "/admin/people/new_legislator/";
    const {state, name, district, chamber} = this.state;
    const personData = {
      state,
      name,
      district,
      chamber,
    };

    fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify({"person_data":personData}),
    }).then(response => {
      this.setState({submitSuccess: true});
      return response.json();
    }).catch(error => {
      console.log(error);
    })
    event.preventDefault();
  }

  render() {
    const { submitSuccess } = this.state;

    return(
      <div>
      {submitSuccess ? (
        <div>
          <p>New legislator added successfully.</p>
          <a className="button button--primary" href="/admin/people">Back to Jurisdictions</a>
        </div>
        ) : (
        <form onSubmit={this.handleSubmit}>
          <label> Name:
            <input type="text" name="name" id="name" required onChange={this.handleInputChange}/>
          </label>
          <label> District:
            <input type="text" name="district" id="district" required onChange={this.handleInputChange}/>
          </label>
          <label> Chamber:
            <select name="chamber" id="chamber" value={this.state.chamber} required onChange={this.handleInputChange}>
              <option value="house">House</option>
              <option value="senate">Senate</option>
            </select>
          </label>
          <input type="submit" className="button--primary button" value="Submit" />
          <a className="button" href="/admin/people">Cancel</a>
        </form>
        )}
      </div>
    )
  }
}

export default NewPersonForm;

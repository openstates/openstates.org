import React from 'react';
import Cookies from "js-cookie";

class RetireForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      submitSuccess: false,
      retirementDate: null,
      reason: null,
      isDead: false,
      vacantSeat: false,
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
    const url = "/admin/people/retire/";
    const {retirementDate, isDead, vacantSeat} = this.state;
    const reason =  this.state.isDead ? 'Death' : this.state.reason;
    const retireData = {
      "name": this.props.name,
      "id": this.props.id,
      retirementDate,
      reason,
      isDead,
      vacantSeat,
    };

    fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify(retireData),
    }).then(response => {
      this.setState({submitSuccess: true});
      return response.json();
    }).catch(error => {
      console.log(error);
    });
    event.preventDefault();
  }

  render() {
    const { submitSuccess } = this.state;

    return(
      <div>
      {submitSuccess ? (
        <p>Retirement data saved successfully.</p>
        ) : (
      <form onSubmit={this.handleSubmit}>
        <label> Retirement Date:
          <input type="date" name="retirementDate" id="retirementDate" required onChange={this.handleInputChange}/>
        </label>
        <br />
        <label>Reason for Retirement:
          <input type="text" id="reason" name="reason" onChange={this.handleInputChange}/>
        </label>
        <br />
        <label>
          Dead?
          <input
            name="isDead"
            type="checkbox"
            checked={this.state.isDead}
            onChange={this.handleInputChange} />
        </label>
        <label>
          Did they leave a vacancy?
          <input
            name="vacantSeat"
            type="checkbox"
            checked={this.state.vacantSeat}
            onChange={this.handleInputChange} />
        </label>
        <br />
        <input type="submit" className="button--primary button" value="Submit" />
      </form>
        )}
      </div>
    )
  }

}

export default RetireForm;

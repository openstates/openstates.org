import React from 'react';
import Cookies from "js-cookie";

class DuplicateSponsors extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      submitSuccess: false,
      state: this.props.state,
      sponsors: ['sponsorGroup0'],
      matchRequests: []
    }
    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.pullFormData = this.pullFormData.bind(this);
    this.addNewSponsorGroup = this.addNewSponsorGroup.bind(this);
  }

  handleSubmit(event) {
    const csrftoken = Cookies.get("csrftoken");
    const url = "/admin/people/update/duplicate_sponsors/";
    const sponsorData = this.pullFormData();

    fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify(sponsorData),
    }).then(response => {
      this.setState({submitSuccess: true});
      return response.json();
    }).catch(error => {
      console.log(error);
    })
    event.preventDefault();
  }

  addNewSponsorGroup(event) {
    event.preventDefault();
    let sponsorDivs = [...this.state.sponsors];
    sponsorDivs.push(`sponsorGroup${sponsorDivs.length}`);
    this.setState({sponsors: sponsorDivs });
  }

  pullFormData() {
    const requested = [];
    const sponsors = [...this.state.sponsors];
    sponsors.forEach((sponsor) => {
      const parent = document.getElementById(sponsor);
      const request = {};
      parent.childNodes.forEach(child => {
        const select = child.childNodes[1];
          const { name, value } = select;
          const sponsorName = value.split(': ')[0];
          const sponsorId = value.split(': ')[1];
          request[`${name}Name`] = sponsorName;
          request[`${name}Id`] = sponsorId;
      });
      requested.push({ ...request });
    });
    return requested;
  }

  render() {
    const { submitSuccess } = this.state;
    const options = this.props.state_sponsors.map((sponsor) => {
          const value = `${sponsor.name }: ${sponsor.id}`;
          return <option value={value}>{value}</option>});
    const sponsorGroups = this.state.sponsors.map((sponsor) => {
           return <div className="sponsorGroup" id={sponsor}>
              <label>First Sponsor:
                <select className="firstSponsor" name="first">{options}</select>
              </label>
              <label>Second Sponsor:
                <select className="secondSponsor" name="second">{options}</select>
              </label>
             <hr/>
            </div>
          });

    return(
      <div>
      {submitSuccess ? (
        <div>
          <p>Sponsor edits submitted successfully.</p>
          <a className="button button--primary" href="/admin/people">Back to Jurisdictions</a>
        </div>
        ) : (
        <form onSubmit={this.handleSubmit}>
          {sponsorGroups}
          <input type="submit" className="button--primary button" value="Submit" />
          <input type="submit" className="button" value="Add Another Match" onClick={this.addNewSponsorGroup}/>
          <a className="button" style={{float: 'right'}} href="/admin/people">Cancel</a>
        </form>
        )}

      </div>
    )
  }
}

export default DuplicateSponsors;
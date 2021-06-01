import React from "react";
import PeopleModal from "./people-modal";
import RetireForm from "./retire-form";
import Cookies from "js-cookie";

const fieldOptions = {
  "Name": "name",
  "Title": "title",
  "District": "district",
  "Party": "party",
  "Image": "image",
  "Email": "email",
  "Capitol Phone": "capitol_voice",
  "Capitol Address": "capitol_address",
  "Capitol Fax": "capitol_fax",
  "District Phone": "district_voice",
  "District Address": "district_address",
  "District Fax": "district_fax",
  "Twitter": "twitter",
  "Facebook": "facebook",
  "Instagram": "instagram",
  "Youtube": "youtube",
};
const updatedPeople = [];

export default class PeopleList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      bulkEdit: false,
      showModal: false,
      currentPerson: '',
      currentId: '',
    };
  }

  renderRows(props) {
      let tds = [];
      const {id, name} = props.person;
      if (!this.state.bulkEdit) {
        for (let field of props.fields) {
          tds.push(<td>{props.person[fieldOptions[field]]}</td>);
        }
        tds.push(<td><button className="button" value={id} onClick={() => this.handleClick({id, name})}>Retire</button></td>);
      } else {
        tds.push(<td>{name}</td>);
        for (let field of props.fields) {
          const oldValue = props.person[fieldOptions[field]];
          const fieldOption = fieldOptions[field];
          const fieldId = id + '.' + fieldOption;
          if (fieldOption !== "name") {
            tds.push(<td><input type="text" name={fieldOption} id={fieldId} defaultValue={oldValue} onBlur={this.handleInputChange} /></td>);
          }
        }
      }
      return (
       <tr key={id}>
        {tds}
       </tr>
      );
  }

   handleInputChange(event) {
    const { value, name, id, defaultValue } = event.target;
    // pull id for person
    const personId = id.split('.')[0];

    // add person to updated array or push new one
    if (defaultValue !== value) {
      const personUpdatedIndex = updatedPeople.findIndex(p => p.id === personId);
      if (personUpdatedIndex === -1) {
        updatedPeople.push({
          id: personId,
          [name]: value
        });
      } else {
        updatedPeople[personUpdatedIndex][name] = value;
      }
    }
  }

  handleSaveEdits() {
    const csrftoken = Cookies.get("csrftoken");
    const url = "/admin/people/bulk/";
    const updateData = updatedPeople;

    fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify(updateData),
    }).then(response => {
      this.setState({bulkEdit: false});
      return response.json();
    }).catch(error => {
      console.log(error);
    });
    event.preventDefault();
  }

  handleClick(i) {
    this.setState({
      showModal: !this.state.showModal,
      currentPerson: i.name,
      currentId: i.id,
    });
  }

  closeModal() {
    this.setState({
      showModal: !this.state.showModal,
      currentPerson: '',
      currentId: '',
    });
  }

  render() {
    const fields = this.state.bulkEdit ?
      ["Name", "Image", "Capitol Phone", "Capitol Address", "District Phone", "District Address", "Twitter", "Facebook", "Instagram", "Youtube"]
      : ["Name", "Title", "District", "Party"];
    const rows = this.props.current_people.map((p) =>
      this.renderRows({person: p, fields})
    );
    const headers = fields.map((f) => <th key={f}>{f}</th>);
    const { showModal, currentPerson, currentId, bulkEdit } = this.state;

    return (
      <div>
        {bulkEdit ? (
          <div>
            <button className="button button--primary"
                    onClick={() => this.handleSaveEdits()}>Save Edits</button>
            <button className="button" style={{float: 'right'}}
                    onClick={() => this.setState({bulkEdit: false})}>Cancel Edit</button>
          </div>
          ) :
            <button className="button button--primary" style={{float: 'right'}} onClick={() => this.setState({bulkEdit: true})}>Bulk Edit</button>
        }
        {showModal ? (
            <PeopleModal>
                <div>
                  <h3>Would you like to retire {currentPerson}?</h3>
                  <RetireForm name={currentPerson} id={currentId} onSubmit={this.closeModal}/>
                </div>
              <button className="button" onClick={() => this.closeModal()} name="cancel">
                  Close</button>
            </PeopleModal>
          ) : null}
        <table>
          <thead>
          <tr>
            {headers}
          </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    );
  }
}

import React from "react";
import PeopleModal from "./people-modal";
import Cookies from "js-cookie";

export default class PeopleDeltaList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      showModal: false,
    };
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
    const rows = this.props.people.map((p) =>
      <p>OS ID: {{ p.person_id }} Data Changes: {{ p.data_changes }}</p>
    );
    const headers = fields.map((f) => <th key={f}>{f}</th>);
    const { showModal } = this.state;

    return (
      <div>
        {showModal ? (
            <PeopleModal>
                <div>
                  <h3>PR Successfully Submitted</h3>
                </div>
              <button className="button" onClick={() => this.closeModal()} name="cancel">
                  Back to People Admin</button>
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

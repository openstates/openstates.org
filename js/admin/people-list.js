import React from "react";
import PeopleModal from "./people-modal";
import RetireForm from "./retire-form";

const fieldOptions = {
  "Name": "name",
  "Title": "title",
  "District": "district",
  "Party": "party",
  "Email": "email",
};

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
      for (let field of props.fields) {
        tds.push(<td>{props.person[fieldOptions[field]]}</td>);
      }
      tds.push(<td><button className="button" value={id} onClick={() => this.handleClick({id, name})}>Retire</button></td>);
      return (
       <tr key={id}>
        {tds}
       </tr>
      );
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
      ["Name", "Title", "District", "Party", "Email"]
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
                    onClick={() => this.setState({bulkEdit: false})}>Save Edits</button>
            <button className="button" style={{float: 'right'}}
                    onClick={() => this.setState({bulkEdit: false})}>Cancel Edit</button>
          </div>
          ) : <button className="button button--primary" onClick={() => this.setState({bulkEdit: true})}>Bulk Edit</button>}
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

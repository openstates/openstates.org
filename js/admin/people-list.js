import React from "react";
import RetireModal from "./retire-modal";
import RetireForm from "./retire-form";

const fieldOptions = {
  "Name": "name",
  "Title": "title",
  "District": "district",
  "Party": "party",
};

export default class PeopleList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      showModal: false,
      currentPerson: '',
      currentId: '',
    };
  }

  renderRows(props) {
      let tds = [];
      for(let field of props.fields) {
         tds.push(<td>{props.person[fieldOptions[field]]}</td>);
      }
      const {id, name} = props.person;
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
    const fields = ["Name", "Title", "District", "Party"];
    const rows = this.props.current_people.map((p) =>
      this.renderRows({person: p, fields})
    );
    const headers = fields.map((f) => <th key={f}>{f}</th>);
    const { showModal, currentPerson, currentId } = this.state;

    return (
      <div>
        {showModal ? (
            <RetireModal>
              <h3>Would you like to retire {currentPerson}?</h3>
              <RetireForm name={currentPerson} id={currentId} onSubmit={this.closeModal}/>
              <button className="button" onClick={() => this.closeModal()} name="cancel">
                  Close</button>
            </RetireModal>
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

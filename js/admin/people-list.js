import React from "react";
import PeopleModal from "./people-modal";
import RetireForm from "./retire-form";
import EditPerson from "./edit-person";

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
          if (field !== "Name") {
            tds.push(<td><EditPerson props={props.person[fieldOptions[field]]}/></td>);
          }
        }
      }
      return (
       <tr key={id}>
        {tds}
       </tr>
      );
  }

  // const editableField = ({
  //   value: initialValue
  // }) => {
  //   const [value, setValue] = React.useState(initialValue);
  //
  //   const onChange = (e) => {
  //     setValue(e.target.value)
  //   }
  //
  //   React.useEffect(() => {
  //     setValue(initialValue)
  //   }, [initialValue])
  //
  //   return <input type="text" value={value} defaultValue={value} onChange={onChange} />
  // }

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
                    onClick={() => this.setState({bulkEdit: false})}>Save Edits</button>
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

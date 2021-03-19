import _ from "lodash";
import React from "react";
import ReactDOM from "react-dom";

const fieldOptions = {
  "Name": "name",
  "Title": "title",
  "District": "district",
  "Party": "party",
};

function PersonRow(props) {
  console.log(props.person);
  let tds = [];
  for(let field of props.fields) {
    tds.push(<td>{props.person[fieldOptions[field]]}</td>);
  }
  return (
    <tr key={props.person.id}>
      {tds}
    </tr>
  );
}

export default function PeopleList(props) {
  const fields = ["Name", "Title", "District", "Party"];
  const rows = props.current_people.map((p) => PersonRow({person: p, fields}));
  const headers = fields.map((f) => <th key={f}>{f}</th>);
  return (
    <table>
      <thead>
        <tr>
          {headers}
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  );
}

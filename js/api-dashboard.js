import React, { PureComponent } from "react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import randomColor from "randomcolor";

const COLORS = {
  graphql: "#6c5bc1",
  "v3": "#028AOF",
};

class EndpointChart extends PureComponent {
  render() {
    return (
      <BarChart
        width={1000}
        height={300}
        data={this.props.data}
        margin={{
          top: 5,
          right: 30,
          left: 20,
          bottom: 5,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="graphql" stackId="a" fill={COLORS["graphql"]} />
        <Bar dataKey="v3" stackId="d" fill={COLORS["v3"]} />
      </BarChart>
    );
  }
}

class KeyChart extends PureComponent {
  render() {
    const lines = this.props.mostCommon
      .slice(0, 15)
      .map(k => (
        <Line
          key={k[0]}
          type="monotone"
          dataKey={k[0]}
          activeDot={{ r: 8 }}
          stroke={randomColor({ seed: k[0] })}
        />
      ));
    return (
      <LineChart
        width={1000}
        height={800}
        data={this.props.data}
        margin={{
          top: 5,
          right: 30,
          left: 20,
          bottom: 5,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        {lines}
      </LineChart>
    );
  }
}

export default class APIDashboard extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    const rows = this.props.most_common.map(k => (
      <tr>
        <td>{k[0]}</td>
        <td>{k[1]}</td>
        <td>{this.props.v2_totals[k[0]]}</td>
        <td>{this.props.v3_totals[k[0]]}</td>
      </tr>
    ));

    return (
      <div>
        <div className="numeric-summary">
          <div>
            <span>{this.props.total_keys}</span>
            <span>Issued Keys</span>
          </div>
          <div>
            <span>{this.props.active_keys}</span>
            <span>Active Keys</span>
          </div>
          <div>
            <span>{this.props.days}</span>
            <span>Days Included</span>
          </div>
        </div>

        <div>
          <h3 className="header">Key Tiers</h3>
          <table>
            <thead>
              <tr>
                <th>Tier</th>
                <th colSpan={3}>v2 Limits</th>
              </tr>
            </thead>
            <tbody>
              {this.props.key_tiers.map(kobj => (
                <tr key={kobj.name}>
                  <td>{kobj.name}</td>
                  <td>{kobj.v2 ? kobj.v2[0] : 0}/day</td>
                  <td>{kobj.v2 ? kobj.v2[1] : 0}/sec</td>
                  <td>{kobj.v2 ? kobj.v2[2] : 0}/sec burst</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div>
          <h3 className="header">Endpoint Usage</h3>
          <EndpointChart data={this.props.endpoint_usage} />
        </div>

        <div>
          <h3 className="header">Key Usage</h3>
          <KeyChart
            data={this.props.key_usage}
            mostCommon={this.props.most_common}
          />
        </div>

        <div>
          <h3 className="header">All Users</h3>
          <table>
            <thead>
              <tr>
                <th>Key</th>
                <th>All Calls</th>
                <th>v2</th>
                <th>v3</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
      </div>
    );
  }
}

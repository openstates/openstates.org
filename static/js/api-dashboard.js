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

const COLORS = {
  graphql: "#6c5bc1",
  "v1.geo": "#55aa55",
  "v1.bills-detail": "#669999",
  "v1.bills-list": "#407F7F",
  "v1.legislator-detail": "#FFD1AA",
  "v1.legislator-list": "#D49A6A",
  "v1.metadata-detail": "#FFAAAA",
  "v1.metadata-list": "#D46A6A",
  "v1.committees": "#804515",
  "v1.events": "#552700",
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
        <Bar dataKey="v1.geo" stackId="b" fill={COLORS["v1.geo"]} />
        <Bar
          dataKey="v1.bills-detail"
          stackId="c"
          fill={COLORS["v1.bills-detail"]}
        />
        <Bar
          dataKey="v1.bills-list"
          stackId="c"
          fill={COLORS["v1.bills-list"]}
        />
        <Bar
          dataKey="v1.legislator-detail"
          stackId="c"
          fill={COLORS["v1.legislator-detail"]}
        />
        <Bar
          dataKey="v1.legislator-list"
          stackId="c"
          fill={COLORS["v1.legislator-list"]}
        />
        <Bar
          dataKey="v1.metadata-detail"
          stackId="c"
          fill={COLORS["v1.metadata-detail"]}
        />
        <Bar
          dataKey="v1.metadata-list"
          stackId="c"
          fill={COLORS["v1.metadata-list"]}
        />
        <Bar
          dataKey="v1.committees"
          stackId="c"
          fill={COLORS["v1.committees"]}
        />
        <Bar dataKey="v1.events" stackId="c" fill={COLORS["v1.events"]} />
      </BarChart>
    );
  }
}

class KeyChart extends PureComponent {
  render() {
    const lines = this.props.mostCommon
      .slice(0, 15)
      .map(k => (
        <Line key={k[0]} type="monotone" dataKey={k[0]} activeDot={{ r: 8 }} />
      ));
    console.log(lines);
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
    console.log(props);
  }

  render() {
    const rows = this.props.most_common.map(k => (
      <tr>
        <td>{k[0]}</td>
        <td>{k[1]}</td>
      </tr>
    ));

    return (
      <div>
        <div className="numeric-summary">
          <div>
            <span>{this.props.user_count}</span>
            <span>Users</span>
          </div>
          <div>
            <span>{this.props.subscriber_count}</span>
            <span>Subscribing Users</span>
          </div>
          <div>
            <span>{this.props.bill_subscriptions}</span>
            <span>Bill Subscriptions</span>
          </div>
          <div>
            <span>{this.props.query_subscriptions}</span>
            <span>Query Subscriptions</span>
          </div>
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
                <th>Calls</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
      </div>
    );
  }
}

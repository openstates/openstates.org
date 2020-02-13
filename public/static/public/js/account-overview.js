import React, { PureComponent } from "react";
import ReactDOM from "react-dom";
import {
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
} from "recharts";

class DailyChart extends PureComponent {
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
        <XAxis dataKey="day" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="id__count" fill="#82ca9d" name={this.props.name} />
      </BarChart>
    );
  }
}

const COLORS = {
  google: "#179c52",
  facebook: "#3b5998",
  github: "#6f42c1",
  twitter: "#38a1f3",
  openstates: "#eb8552",
  weekly: "#2cceb0",
  daily: "#00abff",
};

class ColoredPie extends PureComponent {
  render() {
    return (
      <PieChart width={350} height={350}>
        <Pie
          dataKey="value"
          isAnimationActive={false}
          data={this.props.data}
          cx={150}
          cy={150}
          outerRadius={80}
          fill="#8884d8"
          label
        >
          {this.props.data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[entry.name]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    );
  }
}

export default class AccountsOverview extends React.Component {
  constructor(props) {
    super(props);
    console.log(props);
  }

  render() {
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
          <h3 className="header">Signups</h3>
          <DailyChart data={this.props.users_by_day} name="Signups" />
        </div>

        <div>
          <h3 className="header">Registrations</h3>
          <ColoredPie data={this.props.providers} />
          <h3 className="header">Email Frequency</h3>
          <ColoredPie data={this.props.email_frequencies} />
        </div>

        <div>
          <h3 className="header">Notifications</h3>
          <DailyChart
            data={this.props.notifications_by_day}
            name="Notifications"
          />
        </div>
      </div>
    );
  }
}

window.addEventListener("load", () => {
  const div = document.querySelector('[data-hook="account-overview"]');
  if (div) {
    var context = JSON.parse(document.getElementById("context").textContent);
    ReactDOM.render(React.createElement(AccountsOverview, context), div);
  }
});

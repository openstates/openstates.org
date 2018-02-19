const path = require("path")
const BundleTracker = require('webpack-bundle-tracker')

module.exports = {
  entry: './public/static/js/index',
  output: {
      path: path.resolve('./public/static/bundles'),
      filename: "[name]-[hash].js",
  },

  module: {
    loaders: [
      { test: /\.jsx?$/, exclude: /node_modules/, loader: 'babel-loader'},
    ],
    rules: [{
        test: /\.scss$/,
        use: [{
            loader: "style-loader"
        }, {
            loader: "css-loader"
        }, {
            loader: "sass-loader"
        }]
    }]
  },

  plugins: [
    new BundleTracker({filename: './webpack-stats.json'}),
  ]
}

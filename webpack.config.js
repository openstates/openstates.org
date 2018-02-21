const path = require("path")
const BundleTracker = require('webpack-bundle-tracker')
const LiveReloadPlugin = require('webpack-livereload-plugin')


module.exports = {
  entry: './public/static/js/index',
  output: {
      path: path.resolve('./public/static/bundles'),
      filename: "[name]-[hash].js",
  },

 	devtool: "source-map", // enable source-maps
  module: {
    loaders: [
      { test: /\.jsx?$/, exclude: /node_modules/, loader: 'babel-loader'},
    ],
    rules: [{
        test: /\.scss$/,
        use: [{
            loader: "style-loader"
        }, {
            loader: "css-loader", options: {
              sourceMap: true
            }
        }, {
            loader: "sass-loader", options: {
              includePaths: [path.resolve(__dirname, 'node_modules')],
              sourceMap: true
            }
        }]
    }]
  },

  plugins: [
    new BundleTracker({filename: './webpack-stats.json'}),
    new LiveReloadPlugin({appendScriptTag: 'true'}),
  ]
}

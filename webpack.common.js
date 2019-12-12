const path = require("path")
const BundleTracker = require('webpack-bundle-tracker')
const CleanWebpackPlugin = require('clean-webpack-plugin');

const output_dir = 'public/static/public/bundles'


module.exports = {
  entry: {
    main: ['babel-polyfill', './public/static/public/js/index'],
    fyl: ['./public/static/public/js/find-your-legislator'],
    state_map: ['./public/static/public/js/state-map'],
    district_map: ['./public/static/public/js/legislator-map.js'],
  },
  output: {
    path: path.resolve(output_dir),
    filename: "[name]-[hash].js",
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        loader: "babel-loader",
        query: { plugins: ['transform-runtime'] } 
      },
      {
        test: /\.scss$/,
        use: [
          { loader: "style-loader", options: {sourceMap: true} },
          { loader: "css-loader" },
          { loader: "sass-loader", options: { 
            //includePaths: [path.resolve(__dirname, 'node_modules')],
            sourceMap: true
          } }, 
        ]
      },
      { test: /\.css$/, use: [{loader: "css-loader"}] },
    ]
  },
  plugins: [
    new BundleTracker({filename: './webpack-stats.json'}),
    new CleanWebpackPlugin([output_dir], {watch: true})
  ],
  // optimization: {
  //   splitChunks: {
  //     chunks: 'all',
  //   }
  // }
}

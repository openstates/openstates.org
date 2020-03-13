const path = require("path")
const BundleTracker = require('webpack-bundle-tracker')
const CleanWebpackPlugin = require('clean-webpack-plugin');

const output_dir = 'static/bundles'


module.exports = {
  entry: {
    main: ['babel-polyfill', './static/js/index'],
    common_components: ['./static/js/common-components'],
    fyl: ['./static/js/find-your-legislator'],
    state_map: ['./static/js/state-map'],
    district_map: ['./static/js/legislator-map'],
    account_overview: ['./static/js/account-overview'],
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
      {
        test: /\.(woff(2)?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
        use: [
          {
            loader: 'file-loader',
            options: {
              name: '[name].[ext]',
              outputPath: 'fonts/'
            }
          }
        ]
      }
    ],
  },
  plugins: [
    new BundleTracker({filename: './webpack-stats.json'}),
    new CleanWebpackPlugin([output_dir], {watch: true})
  ],
}

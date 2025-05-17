const path = require('path')
// const ModuleScopePlugin = require("react-dev-utils/ModuleScopePlugin");

module.exports = {
  webpack: {
    alias: {
      'react': path.resolve(__dirname, './node_modules/react'),
      'react-router-dom': path.resolve(__dirname, './node_modules/react-router-dom'),
    },
/*
    configure: webpackConfig => {
      webpackConfig.resolve.plugins = webpackConfig.resolve.plugins.filter(plugin => {
        return !(plugin instanceof ModuleScopePlugin)
      })
      return webpackConfig;
    }
*/
  },
}

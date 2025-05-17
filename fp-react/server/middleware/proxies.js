const proxyMiddleware = require('http-proxy-middleware')
const config = require('../config')
const isAuthenticated = require('../modules/pml-oauth').isAuthenticated
const logger = require('pml-trace-logging').consoleLogger.child({module: require('path').basename(__filename)})

module.exports = function(app) {
  if (config.server.proxies) {
    config.server.proxies.forEach(proxy => {
      let middleWares

      proxy.options.onProxyReq = onProxyReq

      middleWares = [
        proxyMiddleware(proxy.options),
      ]

      if (config.common.env !== 'localhostXXX') { // allow unauth proxy calls in development for debugging
        middleWares.unshift(isAuthenticated) // unshift puts this check BEFORE the proxy middleware
      }

      app.use(proxy.localPath, middleWares)
    })
  }
}

function onProxyReq(proxyReq, req) { // res is available as third inbound parameter, if needed
  if (req.reqAuth && req.reqAuth.headers) {
    Object.keys(req.reqAuth.headers).forEach(header => {
      proxyReq.setHeader(header, req.reqAuth.headers[header])
    }) // add PML request trace headers to outbound proxied requests
  } else {
    logger.warn('PML Trace middleware not functioning')
  }
}
